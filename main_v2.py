import os,sys
import pandas as pd
from pathlib import Path
from sqlalchemy.orm import aliased, sessionmaker
from sqlalchemy import create_engine, text, Table, Column, Integer, String, MetaData, select, or_, and_
import csv
from logging import getLogger, StreamHandler, Formatter, INFO
# Our functions
from extract_data import get_patent_country_code
from get_priority import get_priority_auth
from get_classes import get_classes_cpc, get_classes_ipc
from get_main_table import main_table
from connect_database import create_sqlalchemy_session
import config  

# Set up logging
logger = getLogger(__name__)
handler = StreamHandler()
formatter = Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(INFO)

# Working directory
working_dir = Path("C:/Users/iao/Desktop/PatStat_videre2/Patent_Familier_2024/patent_analyse/")

# Constants
country_code    = "NO"
start_year      = 2019
end_year        = 2023

#Update config.py with constants
config_path     = working_dir / "config.py"


# Create a working forlder in basis of Constants, to store data
def create_data_folder(country_code, start_year, end_year):
    """Create a folder and update the output_dir in config.py."""
    folder_name = f"dataTable_{country_code}_{start_year}_{end_year}"
    output_dir = Path(r"C:\Users\iao\Desktop\PatStat_videre2\Patent_Familier_2024\patent_analyse") / folder_name
    output_dir.mkdir(parents=True, exist_ok=True)

    # Update config.py with the new output_dir
    config_path = Path(__file__).parent / "config.py"  # Path to config.py
    with open(config_path, "r") as f:
        lines = f.readlines()

    # Find the line containing 'output_dir =' and update it
    with open(config_path, "w") as f:
        updated = False
        for line in lines:
            if line.startswith("output_dir"):
                f.write(f'output_dir = r"{output_dir}"\n')  # Use raw string here
                updated = True
            else:
                f.write(line)
        if not updated:  # If no line was found, append the new output_dir
            f.write(f'output_dir = r"{output_dir}"\n')

    print(f"Updated config.py with output_dir: {output_dir}")
    return output_dir

output_dir = create_data_folder(country_code, start_year, end_year)
 
# Update config.py 
config_path = Path(__file__).parent / "config.py"  # Path to config.py
with open(config_path, "r") as f:
    lines = f.readlines()

#Update config.py with constants
with open(config_path, "w") as f:
    updated = False
    for line in lines:
        if line.startswith("country_code"):
            f.write(f'country_code = "{country_code}"\n')  # Use raw string here
            updated = True
        elif line.startswith("start_year"):
            f.write(f'start_year = {start_year}\n')  # Use raw string here
            updated = True
        elif line.startswith("end_year"):
            f.write(f'end_year = {end_year}\n')  # Use raw string here
            updated = True
        else:
            f.write(line) 

# Database session
db = create_sqlalchemy_session()

# Store DataFrame into database
def store_df_to_db(df, table_name):
    try:
        df.to_sql(
            table_name,     # table name
            engine,
            if_exists='replace',    # 'replace' will drop existing table, use 'append' to add data
            index=False,
            schema='dbo'           # default schema for MS SQL Server
        )
        print(f"Successfully added {table_name} to the database.")
    except Exception as e:
        print(f"An error occurred while adding {table_name} to the database: {e}")


def check_file_exists(file_prefix: str) -> bool:
    """Check if a file with the given prefix exists in the output directory."""
    return any(f.startswith(file_prefix) for f in os.listdir(output_dir))


def extract_country_data():
    """Extract data for applicants/inventors from a specific country."""
    """ during the extraction we create family_ids and save it in a file of docdb_family_id.csv."""
    file_prefix = f"country_{country_code}_{start_year}_{end_year}"
    if not check_file_exists(file_prefix):
        logger.info(f"Extracting data for {country_code} ({start_year}-{end_year})...")
        get_patent_country_code(start_year, end_year, country_code, output_dir)
    else:
        logger.info(f"Data table for country_{country_code}_{start_year}_{end_year} already exists. Skipping extraction.")

def process_main_table():
    """Process the main table dataset."""
    family_ids_path = output_dir / "docdb_family_id_1appl_1invt.csv"
    if not family_ids_path.exists():
        logger.error("File 'docdb_family_id_1appl_1invt.csv' not found. Cannot proceed.")
        return

    family_ids = pd.read_csv(family_ids_path)['docdb_family_id'].tolist()
    file_prefix = "main_table_1appl_1invt"  # this will also check for invt50
    if not check_file_exists(file_prefix):
        logger.info("Processing main table dataset...")
        main_table(family_ids, output_dir)
    else:
        logger.info("Main table dataset already exists. Skipping processing.")

def process_priority_auth():
    """Process priority authority data."""
    family_ids_1appl_1invt = output_dir / "docdb_family_id_1appl_1invt.csv"
    if not family_ids_1appl_1invt.exists():
        logger.error("File 'docdb_family_id_1appl_1invt.csv' not found. Cannot proceed.")
        return

    family_ids = pd.read_csv(family_ids_1appl_1invt)['docdb_family_id'].tolist()
    file_prefix = "ids_priority_auth_1appl_1invt.csv"
    if not check_file_exists(file_prefix):
        logger.info("Processing priority authority data...")
        get_priority_auth(family_ids, all=True)
    else:
        logger.info("Priority authority data already exists. Skipping processing.")
    
    # The same for 50 inventors
    family_ids_50_invt = output_dir / "docdb_family_id_50_invt.csv"
    if not family_ids_50_invt.exists():
        logger.error("File 'docdb_family_id_50_invt.csv' not found. Cannot proceed.")
        return

    family_ids = pd.read_csv(family_ids_50_invt)['docdb_family_id'].tolist()
    file_prefix = "ids_priority_auth_50_invt.csv"
    if not check_file_exists(file_prefix):
        logger.info("Processing priority authority data...")
        get_priority_auth(family_ids, all=False)
    else:
        logger.info("Priority authority data already exists. Skipping processing.")

def merge_priority_auth():
    """Merge priority authority data with the main table."""
    main_table_path = output_dir / "main_table_1appl_1invt.csv"
    priority_auth_path = output_dir / "ids_priority_auth_1appl_1invt.csv"

    if not main_table_path.exists() or not priority_auth_path.exists():
        logger.error("Required files for merging main table with priority auth data not found. Cannot proceed.")
        return

    df_main = pd.read_csv(main_table_path)
    df_priority = pd.read_csv(priority_auth_path)

    logger.info("Merging priority authority data with main table...")
    df_merged = df_main.merge(df_priority[['docdb_family_id', 'priority_auth']], on='docdb_family_id', how='left')
    df_merged.to_csv(output_dir / "main_table_merge_1appl_1invt.csv", index=False)

    # The same for 50 inventors
    main_table_path = output_dir / "main_table_50_invt.csv"
    priority_auth_path = output_dir / "ids_priority_auth_50_invt.csv"

    if not main_table_path.exists() or not priority_auth_path.exists():
        logger.error("Required files for merging main table with priority auth data not found. Cannot proceed.")
        return

    df_main = pd.read_csv(main_table_path)
    df_priority = pd.read_csv(priority_auth_path)

    logger.info("Merging priority authority data with main table...")
    df_merged = df_main.merge(df_priority[['docdb_family_id', 'priority_auth']], on='docdb_family_id', how='left')
    df_merged.to_csv(output_dir / "main_table_merge_50_invt.csv", index=False)

 
def process_classes():
    """Process CPC and IPC classes."""
    file_prefix = "ipc_classes_1appl_1invt.csv"
    if not check_file_exists(file_prefix):
        logger.info("Processing CPC and IPC classes...")
        family_ids_path = output_dir / "docdb_family_id_1appl_1invt.csv"
        if not family_ids_path.exists():
            logger.error("File 'docdb_family_id_1appl_1invt.csv' not found. Cannot proceed.")
            return

        family_ids = pd.read_csv(family_ids_path)['docdb_family_id'].tolist()
        batch_size = 100

        cpc_results = get_classes_cpc(family_ids, batch_size)
        ipc_results = get_classes_ipc(family_ids, batch_size)

        df_cpc = pd.DataFrame(cpc_results, columns=['appln_id', 'docdb_family_id', 'cpc_class_symbol'])
        df_ipc = pd.DataFrame(ipc_results, columns=['appln_id', 'docdb_family_id', 'ipc_class_symbol'])

        df_cpc.to_csv(output_dir / "cpc_classes_1appl_1invt.csv", index=False)
        df_ipc.to_csv(output_dir / "ipc_classes_1appl_1invt.csv", index=False)
    else:
        logger.info("CPC and IPC classes already processed. Skipping.")

    # The same for 50 inventors
    file_prefix = "ipc_classes_50_invt.csv"
    if not check_file_exists(file_prefix):
        logger.info("Processing CPC and IPC classes...in 50_invt")
        family_ids_path = output_dir / "docdb_family_id_50_invt.csv"
        if not family_ids_path.exists():
            logger.error("File 'docdb_family_id_50_invt.csv' not found. Cannot proceed.")
            return

        family_ids = pd.read_csv(family_ids_path)['docdb_family_id'].tolist()
        batch_size = 100

        cpc_results = get_classes_cpc(family_ids, batch_size)
        ipc_results = get_classes_ipc(family_ids, batch_size)

        df_cpc = pd.DataFrame(cpc_results, columns=['appln_id', 'docdb_family_id', 'cpc_class_symbol'])
        df_ipc = pd.DataFrame(ipc_results, columns=['appln_id', 'docdb_family_id', 'ipc_class_symbol'])

        df_cpc.to_csv(output_dir / "cpc_classes_50_invt.csv", index=False)
        df_ipc.to_csv(output_dir / "ipc_classes_50_invt.csv", index=False)
    else:
        logger.info("CPC and IPC classes already processed. Skipping.")

# This function get input from <merge_cpc_ipc_classes>
def merge_and_clean_cpc_ipc_classes(cpc_file, ipc_file, output_file):
    """
    Merge and clean CPC and IPC classes for a given dataset.

    Parameters:
        cpc_file (Path): Path to the CPC classes file.
        ipc_file (Path): Path to the IPC classes file.
        output_file (Path): Path to save the merged output file.
    """
    # Check if the output file already exists
    if output_file.exists():
        logger.info(f"File {output_file} already exists. Skipping merging and cleaning of CPC/IPC classes.")
        return

    # Check if required input files exist
    if not cpc_file.exists() or not ipc_file.exists():
        logger.error(f"Required files for cleaning and merging classes not found: {cpc_file}, {ipc_file}. Cannot proceed.")
        return

    # Load DataFrames
    logger.info("Loading CPC and IPC class data...")
    df_cpc = pd.read_csv(cpc_file)
    df_ipc = pd.read_csv(ipc_file)

    # Clean CPC classes
    logger.info("Cleaning CPC class data...")
    df_cpc['cpc_class_symbol'] = df_cpc['cpc_class_symbol'].str.split('/').str[0].str.replace(' ', '')
    df_cpc_grouped = df_cpc.groupby(['appln_id', 'docdb_family_id'])['cpc_class_symbol'].apply(
        lambda x: ', '.join(set(x))
    ).reset_index()

    # Clean IPC classes
    logger.info("Cleaning IPC class data...")
    df_ipc['ipc_class_symbol'] = df_ipc['ipc_class_symbol'].str.split('/').str[0].str.replace(' ', '')
    df_ipc_grouped = df_ipc.groupby(['appln_id', 'docdb_family_id'])['ipc_class_symbol'].apply(
        lambda x: ', '.join(set(x))
    ).reset_index()

    # Merge CPC and IPC classes
    logger.info("Merging CPC and IPC class data...")
    df_merged = pd.merge(df_cpc_grouped, df_ipc_grouped, on=['appln_id', 'docdb_family_id'], how='outer')

    # Save the merged DataFrame to a CSV file
    logger.info(f"Saving merged CPC/IPC class data to {output_file}...")
    df_merged.to_csv(output_file, index=False)

    logger.info("CPC and IPC classes merged and cleaned successfully.")


def merge_cpc_ipc_classes():
    """Merge and clean CPC and IPC classes for both 1appl_1invt and 50_invt datasets."""
    # Process 1appl_1invt dataset
    cpc_path_1appl_1invt = output_dir / "cpc_classes_1appl_1invt.csv"
    ipc_path_1appl_1invt = output_dir / "ipc_classes_1appl_1invt.csv"
    output_path_1appl_1invt = output_dir / "cpc_ipc_merge_classes_1appl_1invt.csv"

    merge_and_clean_cpc_ipc_classes(cpc_path_1appl_1invt, ipc_path_1appl_1invt, output_path_1appl_1invt)

    # Process 50_invt dataset
    cpc_path_50_invt = output_dir / "cpc_classes_50_invt.csv"
    ipc_path_50_invt = output_dir / "ipc_classes_50_invt.csv"
    output_path_50_invt = output_dir / "cpc_ipc_merge_classes_50_invt.csv"

    merge_and_clean_cpc_ipc_classes(cpc_path_50_invt, ipc_path_50_invt, output_path_50_invt)
     
# input parameter come from the main function main_table_merge_classes
def merge_main_table_with_classes(main_table_path, cpc_ipc_classes_path, output_path):
    """
    Merge main table data with CPC/IPC classes data for a given dataset.

    Parameters:
        main_table_path (Path): Path to the main table file.
        cpc_ipc_classes_path (Path): Path to the CPC/IPC classes file.
        output_path (Path): Path to save the merged output file.
    """
    # Check if the output file already exists
    if output_path.exists():
        logger.info(f"File {output_path} already exists. Skipping merging classes with names.")
        return

    # Check if required input files exist
    if not cpc_ipc_classes_path.exists():
        logger.error(f"File {cpc_ipc_classes_path} not found. Cannot proceed with merging classes.")
        return
    if not main_table_path.exists():
        logger.error(f"File {main_table_path} not found. Cannot proceed with merging classes.")
        return

    # Load DataFrames
    logger.info("Loading main table data...")
    df_main = pd.read_csv(main_table_path)
    logger.info("Loading CPC/IPC classes data...")
    df_classes = pd.read_csv(cpc_ipc_classes_path)

    # Merge on 'docdb_family_id'
    logger.info("Merging CPC/IPC classes data with names data...")
    df_merged = pd.merge(
        df_main,
        df_classes,
        on='docdb_family_id',
        how='left'
    )

    # Save the merged DataFrame to a CSV file
    logger.info(f"Saving merged data to {output_path}...")
    df_merged.to_csv(output_path, index=False)
    logger.info("Classes merged with names data successfully.")


def main_table_merge_classes():
    """Merge CPC/IPC classes data with names data for both 1appl_1invt and 50_invt datasets."""
    # Process 1appl_1invt dataset
    main_table_path_1appl_1invt = output_dir / "main_table_merge_1appl_1invt.csv"
    cpc_ipc_classes_path_1appl_1invt = output_dir / "cpc_ipc_merge_classes_1appl_1invt.csv"
    output_path_1appl_1invt = output_dir / "main_table_merge_classes_1appl_1invt.csv"

    merge_main_table_with_classes(main_table_path_1appl_1invt, cpc_ipc_classes_path_1appl_1invt, output_path_1appl_1invt)

    # Process 50_invt dataset
    main_table_path_50_invt = output_dir / "main_table_merge_50_invt.csv"
    cpc_ipc_classes_path_50_invt = output_dir / "cpc_ipc_merge_classes_50_invt.csv"
    output_path_50_invt = output_dir / "main_table_merge_classes_50_invt.csv"

    merge_main_table_with_classes(main_table_path_50_invt, cpc_ipc_classes_path_50_invt, output_path_50_invt)

 
def main_table_merge_all_with_names():
    country_code = config.country_code
    start_year = config.start_year
    end_year = config.end_year
    output_dir = Path(config.output_dir)  

    #Merge names data with the main table.
    main_table_path = output_dir / "main_table_merge_1appl_1invt.csv"
    names_path = output_dir / "country_{country_code}_{start_year}_{end_year}_1appl_1invt.csv"

    if not main_table_path.exists() or not names_path.exists():
        logger.error("Required files for merging names data not found. Cannot proceed.")
        return

    df_main = pd.read_csv(main_table_path)
    df_names = pd.read_csv(names_path)

    logger.info("Merging names data with main table...")
    df_merged = df_main.merge(df_names, on='docdb_family_id', how='left')
    df_merged = df_merged.loc[:, ~df_merged.columns.str.endswith('_y')]
    df_merged.columns = df_merged.columns.str.replace('_x', '', regex=False)
    df_merged.to_csv(output_dir / "main_table_merge_all_1appl_1invt.csv", index=False)

    #Store the merged DataFrame to the database
    logger.info("Storing data into database...")
    store_df_to_db(df_merged, "main_table_1appl_1invt")
    
    #the same for 50 inventors
    main_table_path = output_dir / "main_table_merge_50_invt.csv"
    names_path = output_dir / "country_{country_code}_{start_year}_{end_year}_50_invt.csv"

    if not main_table_path.exists() or not names_path.exists():
        logger.error("Required files for merging names data not found. Cannot proceed.")
        return

    df_main = pd.read_csv(main_table_path)
    df_names = pd.read_csv(names_path)

    logger.info("Merging names data with main table...")
    df_merged = df_main.merge(df_names, on='docdb_family_id', how='left')
    df_merged = df_merged.loc[:, ~df_merged.columns.str.endswith('_y')]
    df_merged.columns = df_merged.columns.str.replace('_x', '', regex=False)
    df_merged.to_csv(output_dir / "main_table_merge_all_50_invt.csv", index=False)
    
    #Store dataframe into database
    logger.info("Storing data into database...")
    store_df_to_db(df_merged, "main_table_50_invt")
  

if __name__ == "__main__":
    logger.info("Starting patent analysis pipeline...")

    try:
        extract_country_data()
        process_main_table()
        process_priority_auth()
        merge_priority_auth()
        process_classes()    
        try:  # tryed this because error: 
          # Call the merge_cpc_ipc_classes function ImportError: sys.meta_path is None, Python is likely shutting down
          logger.info("Starting CPC/IPC class merging process...")
          merge_cpc_ipc_classes()
          logger.info("CPC/IPC class merging process completed successfully.")
        except ImportError as ie:
           logger.error(f"Import error occurred: {ie}", exc_info=True)
        except Exception as e:
           logger.error(f"An unexpected error occurred: {e}", exc_info=True)
        
        main_table_merge_classes()
        main_table_merge_all_with_names()

        logger.info("Pipeline completed successfully.")
    except Exception as e:
        logger.error(f"An error occurred: {e}")