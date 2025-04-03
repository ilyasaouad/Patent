# Main script to process patent data for a specified country and time period.
# Use main.py --country <country_code> --start-year <start_year> --end-year <end_year> --working-dir <working_dir> --save-db
# python main.py --country NO --start-year 2020 --end-year 2020 --working-dir C:/Users/iao/Desktop/PatStat_videre2/Patent_Familier_2024/patent_analyse --save-db
import os
import sys
import pandas as pd
import numpy as np
import argparse
from pathlib import Path
from sqlalchemy import create_engine, text
import logging
from matplotlib import pyplot as plt

# Our functions
from get_applicants_inventors_details import get_applicants_inventors_data
from connect_database import create_sqlalchemy_session
from config import Config  # Import the Config class


# Setup logging
def setup_logging():
    """Configure logging for the application"""
    logger = logging.getLogger(__name__)
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger


logger = setup_logging()


def create_data_folder(country_code, start_year, end_year, working_dir):
    """
    Create a folder for storing data and return the output directory path.
    """
    folder_name = f"dataTable_{country_code}_{start_year}_{end_year}"
    output_dir = working_dir / folder_name
    output_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Created output directory: {output_dir}")
    return output_dir


def store_df_to_db(df, table_name, engine):
    """
    Store DataFrame into the database.
    """
    try:
        df.to_sql(table_name, engine, if_exists="replace", index=False, schema="dbo")
        logger.info(f"Successfully added {table_name} to the database.")
    except Exception as e:
        logger.error(f"Failed to add {table_name} to the database: {e}", exc_info=True)


def save_dataframes_to_csv(dfs, df_names, output_dir):
    """
    Save each DataFrame in the dfs tuple to a CSV file.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    for name, df in zip(df_names, dfs):
        if not df.empty:
            filename = output_dir / f"{name}.csv"
            df.to_csv(filename, index=False)
            logger.info(f"Saved {name} to {filename}")


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Process patent data for a specified country and time period."
    )
    parser.add_argument(
        "--country", type=str, default="NO", help="Country code (default: NO)"
    )
    parser.add_argument(
        "--start-year", type=int, default=2020, help="Start year (default: 2020)"
    )
    parser.add_argument(
        "--end-year", type=int, default=2020, help="End year (default: 2020)"
    )
    parser.add_argument(
        "--working-dir",
        type=str,
        default="C:/Users/iao/Desktop/PatStat_videre2/Patent_Familier_2024/patent_analyse/",
        help="Working directory",
    )
    parser.add_argument("--save-db", action="store_true", help="Save data to database")
    return parser.parse_args()


def main():
    """Main function to process patent data."""
    args = parse_arguments()

    # Set up parameters from arguments
    country_code = args.country
    start_year = args.start_year
    end_year = args.end_year
    working_dir = Path(args.working_dir)

    logger.info(f"------------------ Start processing - from main -----------------")
    logger.info(
        f"Processing data for country: {country_code}, years: {start_year}-{end_year}"
    )

    # Create output directory based on inputs
    output_dir = create_data_folder(country_code, start_year, end_year, working_dir)

    # Update Config with new settings
    Config.update(
        output_dir=str(output_dir),
        country_code=country_code,
        start_year=start_year,
        end_year=end_year,
    )

    try:
        # Get applicants and inventors data using settings from Config
        (
            df_unique_family_ids,
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
            df_app_indiv_counts,
            df_indiv_applicant_ratio,
            num_families_with_indiv,
            ratio_only_indiv,
            df_female_inventor_ratio,
        ) = get_applicants_inventors_data(
            Config.country_code, Config.start_year, Config.end_year
        )

        # Create dfs tuple for easy handling
        dfs = (
            df_unique_family_ids,
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
            df_app_indiv_counts,
            df_indiv_applicant_ratio,
            num_families_with_indiv,
            ratio_only_indiv,
            df_female_inventor_ratio,
        )

        print("female.......<<<<", df_female_inventor_ratio)
        print("num_families_with_indiv", num_families_with_indiv)
        print("ratio_only_indiv", ratio_only_indiv)

        # Define corresponding names
        df_names = [
            "unique_family_ids",
            "appl_invt",
            "appl_invt_agg",
            "applicant_ratios",
            "inventor_ratios",
            "combined_ratios",
            "applicant_counts",
            "inventor_counts",
            "combined_counts",
            "inv_indiv_counts",
            "inv_non_indiv_counts",
            "app_non_indiv_counts",
            "app_indiv_counts",
            "indiv_applicant_ratio",
            "num_families_with_indiv",
            "ratio_only_indiv",
            "female_inventor_ratio",
        ]

        # Save DataFrames to CSV using Config.output_dir
        csv_output_dir = Path(Config.output_dir) / "data" / "applicant_inventors"
        csv_output_dir.mkdir(parents=True, exist_ok=True)  # Ensure directory exists

        for i, (df_item, name) in enumerate(zip(dfs, df_names)):
            # Define filepath for all items
            filepath = csv_output_dir / f"{name}.csv"

            if isinstance(df_item, pd.DataFrame):
                # It's a DataFrame - save it directly
                df_item.to_csv(filepath, index=False)
                print(f"Saved DataFrame '{name}' to {filepath}")
            else:
                # It's a scalar value (like int64) - convert to a simple DataFrame
                value_df = pd.DataFrame({"value": [df_item]})
                value_df.to_csv(filepath, index=False)
                print(f"Saved value '{name}' ({type(df_item).__name__}) to {filepath}")

    except Exception as e:
        logger.error(f"An error occurred during processing: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
