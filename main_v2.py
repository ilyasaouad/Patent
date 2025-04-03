import os
import sys
import pandas as pd
from pathlib import Path
#from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, text
import logging
from matplotlib import pyplot as plt

# Our functions
from get_applicants_inventors_details import get_applicants_inventors_data
#from get_priority import get_priority_auth
#from get_classes import get_ipc_cpc_classes
#from get_main_table import main_table
#from extract_data import get_country
from connect_database import create_sqlalchemy_session
import config



# Initialize Logger
logger = logging.getLogger(__name__)
handler = logging.StreamHandler(sys.stdout)

# Define a detailed formatter that includes file name, line number, and timestamp
formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
)
handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(handler)
logger.setLevel(logging.INFO)


# Constants
country_code = "NO"  # Country code
start_year= 2020    # Start year
end_year = 2020      # End year
 
# Working directory
working_dir= Path("C:/Users/iao/Desktop/PatStat_videre2/Patent_Familier_2024/patent_analyse/")

#######################  Start processing #########################

def create_data_folder(country_code, start_year, end_year):
    """
    Create a folder for storing data and update the `output_dir` in `config.py`.
    """
    folder_name = f"dataTable_{country_code}_{start_year}_{end_year}"
    output_dir = working_dir / folder_name
    output_dir.mkdir(parents=True, exist_ok=True)

    # Update `config.py` with the new `output_dir`
    config_path = working_dir / "config.py"
    with open(config_path, "r") as f:
        lines = f.readlines()

    with open(config_path, "w") as f:
        updated = False
        for line in lines:
            if line.startswith("output_dir"):
                f.write(f'output_dir = r"{output_dir}"\n')
                updated = True
            else:
                f.write(line)
        if not updated:
            f.write(f'output_dir = r"{output_dir}"\n')

    logger.info(f"Updated config.py with output_dir: {output_dir}")
    return output_dir


def store_df_to_db(df, table_name, engine):
    """
    Store DataFrame into the database.
    """
    try:
        df.to_sql(
            table_name,
            engine,
            if_exists='replace',
            index=False,
            schema='dbo'
        )
        logger.info(f"Successfully added {table_name} to the database.")
    except Exception as e:
        logger.error(f"Failed to add {table_name} to the database: {e}", exc_info=True)


def check_file_exists(file_prefix: str) -> bool:
    """
    Check if a file with the given prefix exists in the output directory.
    """
    output_dir = Path(config.output_dir)
    files_in_dir = os.listdir(output_dir)
    return any(f.startswith(Path(file_prefix).name) for f in files_in_dir)


 # The MAIN call start here...

print('------------------ Start processing - from main -----------------')
(   df_unique_family_ids,
    df_appl_invt,
    df_appl_invt_agg,
    df_applicant_ratios,
    df_inventor_ratios,
    df_combined_ratios,
    df_applicant_counts,
    df_inventor_counts,
    df_combined_counts,
    df_inv_indiv_counts,
    df_inv_non_indiv_counts,
    df_app_non_indiv_counts,
    df_app_indiv_counts) = get_applicants_inventors_data(country_code, start_year, end_year)

# Save dfs to files
# Define the directory for CSV files
# Get output_dir from config.py
output_dir = Path(config.output_dir)
output_dir = output_dir / 'data' / 'applicant_inventors'

# Create the directory if it doesn't exist
output_dir.mkdir(parents=True, exist_ok=True)

# Save each DataFrame as a CSV file
for name, df in zip(df_names, dfs):
    if not df.empty:  # Only save non-empty DataFrames
        filename = output_dir / f"{name}.csv"
        df.to_csv(filename, index=False)  # Save without index for cleaner files
        print(f"Saved {name} to {filename}")

 
  



 
 

 
   