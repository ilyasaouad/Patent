import sys
import pandas as pd
import numpy as np
from pathlib import Path
import logging
from matplotlib import pyplot as plt
import streamlit as st
import plotly

# Our functions
from get_applicants_inventors_details import get_applicants_inventors_data
from connect_database import create_sqlalchemy_session
from config import Config  
from prompts import PROMPTS
from llm_analyse import analyze_dataframe
from ploting_applicants_inventors_details import plot_appl_inv_ratios_interactive

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

def main():
    st.title("Patent Data Analysis")

    # Input fields
    country_code = st.text_input("Country Code", value="NO")
    start_year = st.number_input("Start Year", min_value=1900, max_value=2100, value=2020)
    end_year = st.number_input("End Year", min_value=1900, max_value=2100, value=2020)

    # Define working directory
    working_dir = Path("C:/Users/iao/Desktop/PatStat_videre2/Patent_Familier_2024/patent_analyse/")

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

                # Generate figures
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

                # Create a list of dataframes
                dataframes_list = [df_applicant_counts, df_inventor_counts, df_combined_counts]
                dataframe_names = ["applicant_counts", "inventor_counts", "combined_counts"]
                
                prompt_name = "applicants_inventors_count"
                # Get analysis for all dataframes together
                analysis_result = analyze_dataframe(
                dataframes_list,
                dataframe_names,
                prompt_name,
                Config.country_code
                )

                # Save individual analyses
                txt_output_dir = output_dir / "analyse" / "applicants_inventors"
                txt_output_dir.mkdir(parents=True, exist_ok=True)

                for individual in analysis_result["individual_responses"]:
                    df_name = individual["df_name"]
                    response = individual["response"]
                    filepath = txt_output_dir / f"{df_name}_analysis.txt"
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(response)
                    logger.info(f"Saved analysis for '{df_name}' to {filepath}")

                # Save summary
                summary_filepath = txt_output_dir / "appl_inv_summary_analysis.txt"
                with open(summary_filepath, "w", encoding="utf-8") as f:
                    f.write(analysis_result["summary"])
                logger.info(f"Saved summary to {summary_filepath}")

                # Define the directory where plots are saved 
                plots_dir = Path(Config.output_dir) / "plots" / "applicants_inventors"

                # Updated DataFrames dictionary with singular names to match file prefixes
                dataframes = {
                    "applicant_ratio": ("Applicant Ratios", df_applicant_ratios),
                    "inventor_ratio": ("Inventor Ratios", df_inventor_ratios),
                    "combined_ratio": ("Combined Ratios", df_combined_ratios),
                    "applicant_counts": ("Applicant Counts", df_applicant_counts),
                    "inventor_counts": ("Inventor Counts", df_inventor_counts),
                    "inv_indiv_counts": ("Inventor Individual Counts", df_inv_indiv_counts),
                    "inv_non_indiv_counts": ("Inventor Non-Individual Counts", df_inv_non_indiv_counts),
                    "app_indiv_counts": ("Applicant Individual Counts", df_app_indiv_counts),
                    "app_non_indiv_counts": ("Applicant Non-Individual Counts", df_app_non_indiv_counts),
                    "indiv_applicant_ratio": ("Individual Applicant Ratio", df_indiv_applicant_ratio),
                    "female_inventor_ratio": ("Female Inventor Ratio", df_female_inventor_ratio),
                }

                # Function to display a section for a DataFrame
                def display_dataframe_section(df_name, display_name, df):
                    with st.expander(f"### {display_name}", expanded=False):
                        # Display the DataFrame
                        st.write(f"#### {display_name}")
                        st.dataframe(df)

                        # Display related plots
                        st.write("#### Plots")
                        # Look for PNG files
                        png_pattern = f"{df_name}*.png"
                        png_files = list(plots_dir.glob(png_pattern))
                        if png_files:
                            for png_file in png_files:
                                st.image(
                                    str(png_file),
                                    caption=png_file.stem.replace("_", " ").title(),
                                    use_container_width=True,
                                )
                        else:
                            st.write(f"No PNG plots found for '{df_name}' in {plots_dir}.")

                        # Look for HTML files
                        html_pattern = f"{df_name}*.html"
                        html_files = list(plots_dir.glob(html_pattern))
                        if html_files:
                            for html_file in html_files:
                                with open(html_file, "r", encoding="utf-8") as f:
                                    plotly_html = f.read()
                                st.components.v1.html(plotly_html, height=600, scrolling=True)
                                st.caption(html_file.stem.replace("_", " ").title())
                        else:
                            st.write(f"No HTML plots found for '{df_name}' in {plots_dir}.")

                        # Display related analysis
                        st.write("#### Analysis")
                        analysis_file = txt_output_dir / f"{df_name}_analysis.txt"
                        if analysis_file.exists():
                            try:
                                with open(analysis_file, "r", encoding="utf-8") as f:
                                    analysis_content = f.read()
                                st.text_area(
                                    f"Analysis for {display_name}",
                                    value=analysis_content,
                                    height=200,
                                    key=f"analysis_{df_name}"
                                )
                            except Exception as e:
                                st.error(f"Error reading {analysis_file}: {e}")
                        else:
                            st.write(f"No analysis found for '{df_name}' at {analysis_file}.")

                # Main Streamlit layout
                st.title("Processed Data Analysis")

                # Display scalar metrics (outside the expanders)
                st.subheader("Overview")
                st.metric("Number of Families with Individuals", num_families_with_indiv)
                st.metric("Ratio of Families with Only Individuals", f"{ratio_only_indiv:.2f}")

                # Display each DataFrame section
                for df_name, (display_name, df) in dataframes.items():
                    display_dataframe_section(df_name, display_name, df)

                # Success message
                st.success("Data, plots, and analyses have been processed and saved successfully!")

            except Exception as e:
                logger.error(f"An error occurred: {e}", exc_info=True)
                st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
