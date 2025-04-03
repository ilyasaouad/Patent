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

import streamlit as st


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


# Function to create output directory
def create_data_folder(country_code, start_year, end_year, working_dir):
    """
    Create a folder for storing data and return the output directory path.
    """
    folder_name = f"dataTable_{country_code}_{start_year}_{end_year}"
    output_dir = working_dir / folder_name
    output_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Created output directory: {output_dir}")
    return output_dir


# Streamlit app
st.title("Patent Data Analysis")

# Input fields
country_code = st.text_input("Country Code", value="NO")
start_year = st.number_input("Start Year", min_value=1900, max_value=2100, value=2020)
end_year = st.number_input("End Year", min_value=1900, max_value=2100, value=2020)

# Define working directory (consistent with original script)
working_dir = Path(
    "C:/Users/iao/Desktop/PatStat_videre2/Patent_Familier_2024/patent_analyse/"
)

# Button to process data
if st.button("Process Data"):
    with st.spinner("Processing patent data..."):
        try:
            # Log start of processing
            logger.info(
                f"Processing data for country: {country_code}, years: {start_year}-{end_year}"
            )

            # Create output directory
            output_dir = create_data_folder(
                country_code, start_year, end_year, working_dir
            )

            # Update Config with new settings
            Config.update(
                output_dir=str(output_dir),
                country_code=country_code,
                start_year=start_year,
                end_year=end_year,
            )

            # Process data
            dfs = get_applicants_inventors_data(
                Config.country_code, Config.start_year, Config.end_year
            )

            # Unpack the tuple
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
            ) = dfs

            # Define DataFrame names
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

            # Save DataFrames to CSV
            csv_output_dir = output_dir / "data" / "applicants_inventors"
            csv_output_dir.mkdir(parents=True, exist_ok=True)
            for i, (df_item, name) in enumerate(zip(dfs, df_names)):
                filepath = csv_output_dir / f"{name}.csv"
                if isinstance(df_item, pd.DataFrame):
                    df_item.to_csv(filepath, index=False)
                    logger.info(f"Saved DataFrame '{name}' to {filepath}")
                else:
                    value_df = pd.DataFrame({"value": [df_item]})
                    value_df.to_csv(filepath, index=False)
                    logger.info(f"Saved value '{name}' to {filepath}")

            st.success(f"Data processed and saved to {csv_output_dir}")

            # Display results
            st.subheader("Processed Data")

            # Display scalar values
            st.write("### Overview")
            st.metric("Number of Families with Individuals", num_families_with_indiv)
            st.metric(
                "Ratio of Families with Only Individuals", f"{ratio_only_indiv:.2f}"
            )

            # Organize DataFrames in tabs
            tab1, tab2, tab3, tab4 = st.tabs(
                ["Family Data", "Applicant & Inventor", "Ratios", "Counts"]
            )

            with tab1:
                st.write("#### Unique Family IDs")
                st.dataframe(df_unique_family_ids)

            with tab2:
                st.write("#### Applicant and Inventor Data")
                st.dataframe(df_appl_invt)
                st.write("#### Aggregated Applicant and Inventor Data")
                st.dataframe(df_appl_invt_agg)

            with tab3:
                st.write("#### Applicant Ratios")
                st.dataframe(df_applicant_ratios)
                st.write("#### Inventor Ratios")
                st.dataframe(df_inventor_ratios)
                st.write("#### Combined Ratios")
                st.dataframe(df_combined_ratios)
                st.write("#### Individual Applicant Ratio")
                st.dataframe(df_indiv_applicant_ratio)
                st.write("#### Female Inventor Ratio")
                st.dataframe(df_female_inventor_ratio)

            with tab4:
                st.write("#### Applicant Counts")
                st.dataframe(df_applicant_counts)
                st.write("#### Inventor Counts")
                st.dataframe(df_inventor_counts)
                st.write("#### Combined Counts")
                st.dataframe(df_combined_counts)
                st.write("#### Inventor Individual Counts")
                st.dataframe(df_inv_indiv_counts)
                st.write("#### Inventor Non-Individual Counts")
                st.dataframe(df_inv_non_indiv_counts)
                st.write("#### Applicant Non-Individual Counts")
                st.dataframe(df_app_non_indiv_counts)
                st.write("#### Applicant Individual Counts")
                st.dataframe(df_app_indiv_counts)

            # Success message after processing
            st.success("Data and plots have been processed and saved successfully!")

            # Display DataFrames (your existing code)
            st.subheader("Processed Data")
            # (Add your DataFrame displays here, e.g., st.dataframe(df_applicant_counts))

            # Define the directory where plots are saved after update config
            plots_dir = Path(Config.output_dir) / "plots" / "applicants_inventors"

            # Add a section for plots
            st.subheader("Visualizations")
            if plots_dir.exists():
                # Get all PNG files in the plots directory
                plot_files = list(plots_dir.glob("*.png"))
                if plot_files:
                    for plot_file in plot_files:
                        # Display each plot with a caption based on its file name
                        st.image(
                            str(plot_file),
                            caption=plot_file.stem.replace("_", " ").title(),
                        )
                else:
                    st.write("No PNG files found in the plots directory.")
            else:
                st.error(f"Plots directory not found at: {plots_dir}")

        except Exception as e:
            logger.error(f"An error occurred: {e}", exc_info=True)
            st.error(f"An error occurred: {e}")

        #####################
        ###### PLOTLY
        ##################
        # Generate figures
        from ploting_applicants_inventors_details import (
            plot_appl_inv_ratios_interactive,
        )

        figures = plot_appl_inv_ratios_interactive(
            df_applicant_ratios,
            df_inventor_ratios,
            df_combined_ratios,
            sort_by_country="NO",
            max_legend_countries=10,
        )
    # Display in Streamlit
    for ratio_type, fig in figures.items():
        st.subheader(f"{ratio_type.capitalize()} Ratios")
        st.plotly_chart(fig, use_container_width=True)
