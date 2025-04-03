import os
import sys
import pandas as pd
from pathlib import Path
#from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, text
import logging

# Our functions
from extract_data import get_patent_country_code
from get_priority import get_priority_auth
from get_classes import get_ipc_cpc_classes
from get_main_table import main_table
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


# Working directory
WORKING_DIR = Path("C:/Users/iao/Desktop/PatStat_videre2/Patent_Familier_2024/patent_analyse/")


# Constants
COUNTRY_CODE = "NO"  # Country code
START_YEAR = 2020    # Start year
END_YEAR = 2020      # End year
T = 0.5              # Threshold for the percentage of inventors from the country


def create_data_folder(country_code, start_year, end_year):
    """
    Create a folder for storing data and update the `output_dir` in `config.py`.
    """
    folder_name = f"dataTable_{country_code}_{start_year}_{end_year}"
    output_dir = WORKING_DIR / folder_name
    output_dir.mkdir(parents=True, exist_ok=True)

    # Update `config.py` with the new `output_dir`
    config_path = WORKING_DIR / "config.py"
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


def clean_merged_dataframe(df):
    """
    Clean the merged DataFrame by removing `_x` and `_y` suffixes.
    """
    columns_x = [col for col in df.columns if col.endswith('_x')]
    columns_y = [col for col in df.columns if col.endswith('_y')]

    # Drop `_y` columns
    df = df.drop(columns=columns_y)

    # Rename `_x` columns
    df = df.rename(columns={col: col.replace('_x', '') for col in columns_x})

    return df


def process_main_table(engine):
    """
    Process the main table and save it to CSV and the database.
    """
    try:
        # Step 1: Extract applicants/inventors from a specific country
        df_1appl_1invt = get_patent_country_code(T)
        family_ids = df_1appl_1invt['docdb_family_id'].drop_duplicates().tolist()

        # Step 2: Create the main table
        df_main_table = main_table(family_ids)

        # Step 3: Get priority auth and merge
        priority_auth = get_priority_auth(family_ids)
        df_main_prio_names = (
            df_main_table.merge(
                priority_auth[['docdb_family_id', 'priority_auth']],
                on='docdb_family_id',
                how='left'
            )
            .merge(df_1appl_1invt, on='docdb_family_id', how='left')
        )

        # Step 4: Clean the merged DataFrame
        df_main_prio_names = clean_merged_dataframe(df_main_prio_names)

        # Step 5: Save to CSV
        output_dir = Path(config.output_dir)
        df_main_prio_names.to_csv(output_dir / '05_main_table_prio_names.csv', index=False)

        # Step 6: Get IPC/CPC classes and merge
        df_classes = get_ipc_cpc_classes(family_ids)
        df_main_prio_names_class = pd.merge(
            df_main_prio_names,
            df_classes,
            on='appln_id',
            how='left'
        )

        # Step 7: Save to CSV
        df_main_prio_names_class.to_csv(output_dir / '06_main_table_prio_names_classes.csv', index=False)

        # Step 8: Store DataFrame into the database
        table_name = f"country_{COUNTRY_CODE}_{START_YEAR}_{END_YEAR}_main_table"
        store_df_to_db(df_main_prio_names_class, table_name, engine)

    except Exception as e:
        logger.error(f"An error occurred during processing: {e}", exc_info=True)


if __name__ == "__main__":
    try:
        # Update `config.py` with constants
        config_path = WORKING_DIR / "config.py"
        with open(config_path, "r") as f:
            lines = f.readlines()

        with open(config_path, "w") as f:
            updated = False
            for line in lines:
                if line.startswith("country_code"):
                    f.write(f'country_code = "{COUNTRY_CODE}"\n')
                    updated = True
                elif line.startswith("start_year"):
                    f.write(f'start_year = {START_YEAR}\n')
                    updated = True
                elif line.startswith("end_year"):
                    f.write(f'end_year = {END_YEAR}\n')
                    updated = True
                else:
                    f.write(line)

        # Create data folder and update `config.py`
        output_dir = create_data_folder(COUNTRY_CODE, START_YEAR, END_YEAR)

        # Database session
        engine = create_sqlalchemy_session()

        # Process main table
        process_main_table(engine)

    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)