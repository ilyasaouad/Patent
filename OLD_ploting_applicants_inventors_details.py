# For plot def get_applicants_inventors_data in get_applicants_inventors_details.py
import os,sys
import pandas as pd
import numpy as np
from pathlib import Path
from connect_database import create_sqlalchemy_session
from sqlalchemy.orm import aliased
from sqlalchemy import create_engine, text, Table, Column, Integer, String, MetaData, select, or_, and_, case, func, distinct, and_
from sqlalchemy.sql import func
import matplotlib.pyplot as plt
import ast
import unicodedata
import streamlit as st
import re
import config
from typing import Optional


import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import config


output_dir = Path(config.output_dir)




# --- Sub-functions for Ratio Plots ---
def plot_ratio_data(df_final, ratio_type, output_dir, sort_by_country=config.country_code, figsize=(12, 8), dpi=300):
    """Plot and return the percentage table for a given ratio type."""
    MAX_COUNTRIES_IN_LEGEND = 10
    pivot_table = df_final.pivot(index='docdb_family_id', columns='person_ctry_code', values=f'{ratio_type}_ratio').fillna(0)
    percentage_table = pivot_table.div(pivot_table.sum(axis=1), axis=0) * 100
    country_order = percentage_table.mean().sort_values(ascending=False).index
    percentage_table = percentage_table[country_order]
    if sort_by_country in percentage_table.columns:
        percentage_table = percentage_table.sort_values(by=sort_by_country, ascending=False)


    if len(percentage_table.columns) > MAX_COUNTRIES_IN_LEGEND:
        top_countries = percentage_table.columns[:MAX_COUNTRIES_IN_LEGEND]
        others_countries = percentage_table.columns[MAX_COUNTRIES_IN_LEGEND:]
        percentage_table['Others'] = percentage_table[others_countries].sum(axis=1)
        percentage_table = percentage_table.drop(columns=others_countries)
    else:
        top_countries = percentage_table.columns


    percentage_table = percentage_table.reset_index(drop=True)
    percentage_table.index += 1


    # Plotting
    fig, ax = plt.subplots(figsize=figsize)
    bottom = pd.Series(0, index=percentage_table.index)
    colors = plt.cm.tab20.colors


    for i, country in enumerate(percentage_table.columns):
        ax.bar(
            percentage_table.index.astype(str),
            percentage_table[country],
            bottom=bottom,
            label=country if country in top_countries or country == 'Others' else None,
            color=colors[i % len(colors)]
        )
        bottom = bottom + percentage_table[country]


    ax.set_title(f"{ratio_type.capitalize()} Ratio Contribution by Country for Each docdb_family_id", fontsize=14)
    ax.set_xlabel(f"Document Family Index (Sorted by '{sort_by_country}')", fontsize=12)
    ax.set_ylabel("Percentage Contribution (%)", fontsize=12)
    ax.set_xticks(percentage_table.index)
    ax.set_xticklabels(percentage_table.index, fontsize=10)
    ax.legend(title="Country", bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10)
    ax.set_ylim(0, 100 + 20)
    plt.tight_layout()


    # Define and create the full path
    plots_dir = output_dir / 'plots' / 'inventors_applicants_plots'  # Full path relative to output_dir
    plots_dir.mkdir(exist_ok=True, parents=True)  # Create the full directory structure


    # Save the plot
    filename = plots_dir / f"{ratio_type}_ratio_stacked_bar_plot_sorted_by_{sort_by_country}_{config.start_year}_{config.end_year}.png"
    plt.savefig(filename, format='png', dpi=dpi, bbox_inches='tight')
    print(f"Saved {ratio_type} ratio plot as {filename}")
    plt.close()


    return percentage_table


# --- Sub-functions for Count Plots ---
def plot_count_data(df, count_type, output_dir, sort_by_country=config.country_code, figsize=(12, 8), dpi=300):
    """Plot and return the count pivot table for a given count type."""
    if df.empty:
        print(f"No data to plot for {count_type} counts.")
        return None


    MAX_COUNTRIES_IN_LEGEND = 10
    pivot_table = df.pivot(index='docdb_family_id', columns='person_ctry_code', values=f'{count_type}_count').fillna(0)
    if sort_by_country in pivot_table.columns:
        pivot_table = pivot_table.sort_values(by=sort_by_country, ascending=False)
    else:
        pivot_table = pivot_table.sort_index()


    country_totals = pivot_table.sum()
    non_zero_countries = country_totals[country_totals > 0].index
    if len(non_zero_countries) > MAX_COUNTRIES_IN_LEGEND:
        top_countries = non_zero_countries[:MAX_COUNTRIES_IN_LEGEND]
        others_countries = non_zero_countries[MAX_COUNTRIES_IN_LEGEND:]
        pivot_table['Others'] = pivot_table[others_countries].sum(axis=1)
        pivot_table = pivot_table.drop(columns=others_countries)
    else:
        top_countries = non_zero_countries


    pivot_table_plot = pivot_table.reset_index(drop=True)
    pivot_table_plot.index += 1
    indices = pivot_table_plot.index


    # Define color mapping
    all_countries = pivot_table_plot.columns
    colors = plt.cm.tab20.colors
    if len(all_countries) > len(colors):
        extra_colors = plt.cm.tab20b.colors
        colors = list(colors) + list(extra_colors[:len(all_countries) - len(colors)])
    color_map = {country: colors[i] for i, country in enumerate(all_countries)}
    color_map['Others'] = 'gray'


    # Plotting
    fig, ax = plt.subplots(figsize=figsize)
    bottom = pd.Series(0, index=indices)


    if sort_by_country in pivot_table_plot.columns:
        country_sum = pivot_table_plot[sort_by_country].sum()
        if country_sum > 0:
            ax.bar(
                indices,
                pivot_table_plot[sort_by_country],
                bottom=bottom,
                label=sort_by_country if sort_by_country in top_countries else None,
                color=color_map[sort_by_country]
            )
            bottom = bottom + pivot_table_plot[sort_by_country]


    for country in pivot_table_plot.columns:
        if country != sort_by_country:
            country_sum = pivot_table_plot[country].sum()
            if country_sum > 0:
                ax.bar(
                    indices,
                    pivot_table_plot[country],
                    bottom=bottom,
                    label=country if country in top_countries or country == 'Others' else None,
                    color=color_map[country]
                )
                bottom = bottom + pivot_table_plot[country]


    ax.set_title(f"{count_type.capitalize()} Count by Country for Each docdb_family_id", fontsize=14)
    ax.set_xlabel(f"Document Family Index (Sorted by '{sort_by_country}' {count_type.capitalize()}s)", fontsize=12)
    ax.set_ylabel(f"Number of {count_type.capitalize()}s", fontsize=12)
    ax.set_xticks(indices)
    ax.set_xticklabels(indices, fontsize=10)
    ax.legend(title="Country", bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10)
    ax.set_ylim(0, bottom.max() + 3)
    plt.tight_layout()


    plots_dir = output_dir / 'plots' / 'inventors_applicants_plots'  # Full path relative to output_dir
    plots_dir.mkdir(exist_ok=True, parents=True)  # Create the full directory structure


    # Save the plot
    filename =  plots_dir / f"{count_type}_count_stacked_bar_plot_sorted_by_{sort_by_country}_{config.start_year}_{config.end_year}.png"
    plt.savefig(filename, format='png', dpi=dpi, bbox_inches='tight')
    print(f"Saved {count_type} count plot as {filename}")
    plt.close()


    return pivot_table_plot


def plot_inventor_applicant_side_by_side(df_inventor_counts, df_applicant_counts, output_dir, sort_by_country=config.country_code, figsize=(12, 8), dpi=300):
    """Plot a side-by-side bar chart of inventor and applicant counts and return the pivot tables."""
    # Define consistent color mapping
    all_countries = pd.concat([
        df_inventor_counts['person_ctry_code'],
        df_applicant_counts['person_ctry_code']
    ]).unique()
    all_countries.sort()
    colors = plt.cm.tab20.colors
    if len(all_countries) > len(colors):
        extra_colors = plt.cm.tab20b.colors
        colors = list(colors) + list(extra_colors[:len(all_countries) - len(colors)])
    color_map = {country: colors[i] for i, country in enumerate(all_countries)}
    color_map['Others'] = 'gray'


    # Pivot tables for inventors and applicants
    inventor_pivot = df_inventor_counts.pivot(index='docdb_family_id', columns='person_ctry_code', values='inventor_count').fillna(0)
    applicant_pivot = df_applicant_counts.pivot(index='docdb_family_id', columns='person_ctry_code', values='applicant_count').fillna(0)


    # Ensure both pivots have the same index
    all_families = inventor_pivot.index.union(applicant_pivot.index)
    inventor_pivot = inventor_pivot.reindex(all_families, fill_value=0)
    applicant_pivot = applicant_pivot.reindex(all_families, fill_value=0)


    # Sort by total 'sort_by_country' counts (inventors + applicants)
    if sort_by_country in inventor_pivot.columns or sort_by_country in applicant_pivot.columns:
        no_inventors = inventor_pivot.get(sort_by_country, pd.Series(0, index=inventor_pivot.index))
        no_applicants = applicant_pivot.get(sort_by_country, pd.Series(0, index=applicant_pivot.index))
        total_no_counts = no_inventors + no_applicants
        sort_order = total_no_counts.sort_values(ascending=False).index
        inventor_pivot = inventor_pivot.loc[sort_order]
        applicant_pivot = applicant_pivot.loc[sort_order]


    # Plotting
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    bar_width = 0.4
    index = np.arange(len(inventor_pivot))


    # Plot inventor bars (left)
    bottom_inv = np.zeros(len(index))
    if sort_by_country in inventor_pivot.columns:
        country_sum = inventor_pivot[sort_by_country].sum()
        if country_sum > 0:
            ax.bar(
                index,
                inventor_pivot[sort_by_country],
                bar_width,
                bottom=bottom_inv,
                label=sort_by_country,
                color=color_map[sort_by_country]
            )
            bottom_inv += inventor_pivot[sort_by_country]
    for country in inventor_pivot.columns:
        if country != sort_by_country:
            country_sum = inventor_pivot[country].sum()
            if country_sum > 0:
                ax.bar(
                    index,
                    inventor_pivot[country],
                    bar_width,
                    bottom=bottom_inv,
                    label=country if country_sum > 0 and country not in [sort_by_country] else None,
                    color=color_map[country]
                )
                bottom_inv += inventor_pivot[country]


    # Plot applicant bars (right)
    bottom_app = np.zeros(len(index))
    if sort_by_country in applicant_pivot.columns:
        country_sum = applicant_pivot[sort_by_country].sum()
        if country_sum > 0:
            ax.bar(
                index + bar_width,
                applicant_pivot[sort_by_country],
                bar_width,
                bottom=bottom_app,
                label=sort_by_country if sort_by_country not in inventor_pivot.columns else None,
                color=color_map[sort_by_country]
            )
            bottom_app += applicant_pivot[sort_by_country]
    for country in applicant_pivot.columns:
        if country != sort_by_country:  # Fixed typo here
            country_sum = applicant_pivot[country].sum()
            if country_sum > 0:
                already_labeled = country in inventor_pivot.columns and inventor_pivot[country].sum() > 0
                ax.bar(
                    index + bar_width,
                    applicant_pivot[country],
                    bar_width,
                    bottom=bottom_app,
                    label=country if not already_labeled else None,
                    color=color_map[country]
                )
                bottom_app += applicant_pivot[country]


    # Customize the plot
    ax.set_title('Inventors (Left) and Applicants (Right) by Country per docdb_family_id', fontsize=14)
    ax.set_xlabel('Inventors | Applicants', fontsize=12)
    ax.set_ylabel('Count', fontsize=12)
    tick_positions = index + bar_width / 2
    tick_labels = [str(i+1) for i in range(len(inventor_pivot))]
    ax.set_xticks(tick_positions)
    ax.set_xticklabels(tick_labels, rotation=45, ha='right', fontsize=10)
    ax.legend(title="Country", bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10)
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    max_height = max(bottom_inv.max(), bottom_app.max())
    ax.set_ylim(0, max_height + 3)


    plt.tight_layout()


    # Save plot with corrected path
    plots_dir = output_dir / 'plots' / 'inventors_applicants_plots'
    plots_dir.mkdir(exist_ok=True, parents=True)
    filename = plots_dir / f"inventor_applicant_side_by_side_bar_plot_sorted_by_{sort_by_country}_{config.start_year}_{config.end_year}.png"
    plt.savefig(filename, format='png', dpi=dpi, bbox_inches='tight')
    print(f"Saved side-by-side plot as {filename}")
    plt.close()


    # Return plotted pivot tables with 1-based index
    inventor_pivot_plot = inventor_pivot.reset_index(drop=True)
    inventor_pivot_plot.index += 1
    applicant_pivot_plot = applicant_pivot.reset_index(drop=True)
    applicant_pivot_plot.index += 1
    return {'inventor': inventor_pivot_plot, 'applicant': applicant_pivot_plot}


        
def classify_entity(name: str, psn_sector: Optional[str] = None) -> str:
    '''
    Classify a name as 'INDIVIDUAL' or 'NON_INDIVIDUAL' based on psn_sector or naming patterns.
    
    Args:
        name (str): The entity name (e.g., from person_name or psn_name).
        psn_sector (Optional[str]): Existing sector value, if available.
    
    Returns:
        str: 'INDIVIDUAL' or 'NON_INDIVIDUAL'.
    '''
    valid_sectors = {
        'INDIVIDUAL': 'INDIVIDUAL',
        'COMPANY': 'NON_INDIVIDUAL',
        'UNIVERSITY': 'NON_INDIVIDUAL',
        'GOV NON-PROFIT': 'NON_INDIVIDUAL',
        'GOVERNMENT': 'NON_INDIVIDUAL',
        'HOSPITAL': 'NON_INDIVIDUAL',
        'UNKNOWN': None,
        '': None
    }
    
    if psn_sector and psn_sector.strip() in valid_sectors and valid_sectors[psn_sector.strip()] is not None:
        return valid_sectors[psn_sector.strip()]
    
    name = name.strip().upper()
    non_indiv_keywords = [
        'AS', 'ASA', 'INC', 'LTD', 'LLC', 'CORP', 'COMPANY', 'TECHNOLOGIES', 'TECH',
        'UNIVERSITY', 'INSTITUTE', 'GROUP', 'INDUSTRY', 'NORWAY', 'SCANDINAVIA'
    ]
    if any(keyword in name for keyword in non_indiv_keywords):
        return 'NON_INDIVIDUAL'
    
    parts = re.split(r'[,\s]+', name)
    if (',' in name or len(parts) >= 2) and not any(part in non_indiv_keywords for part in parts):
        if any(len(part) <= 2 for part in parts) or len(parts) <= 4:
            return 'INDIVIDUAL'
    
    return 'NON_INDIVIDUAL'


def plot_inventor_applicant_indiv_non_indiv(df_appl_invt_cleaned, output_dir, sort_by_country=config.country_code, figsize=(12, 8), dpi=300):
    """Plot positive/negative bars for individual/non-individual inventors and applicants, returning pivot tables."""
    # Apply classification
    df_appl_invt_cleaned['psn_sector_predicted'] = df_appl_invt_cleaned.apply(
        lambda row: classify_entity(row['person_name'], row['psn_sector']),
        axis=1
    )


    # Categorize Inventors and Applicants
    inv_indiv_data = df_appl_invt_cleaned[
        (df_appl_invt_cleaned['invt_seq_nr'] > 0) & 
        (df_appl_invt_cleaned['psn_sector_predicted'] == 'INDIVIDUAL')
    ].copy()
    df_inv_indiv_counts = (
        inv_indiv_data.groupby(['docdb_family_id', 'person_ctry_code'])
        .agg({'nb_inventors': 'max'})
        .reset_index()
        .rename(columns={'nb_inventors': 'inv_indiv_count'})
    )


    inv_non_indiv_data = df_appl_invt_cleaned[
        (df_appl_invt_cleaned['invt_seq_nr'] > 0) & 
        (df_appl_invt_cleaned['psn_sector_predicted'] == 'NON_INDIVIDUAL')
    ].copy()
    df_inv_non_indiv_counts = (
        inv_non_indiv_data.groupby(['docdb_family_id', 'person_ctry_code'])
        .agg({'nb_inventors': 'max'})
        .reset_index()
        .rename(columns={'nb_inventors': 'inv_non_indiv_count'})
    )


    app_non_indiv_data = df_appl_invt_cleaned[
        (df_appl_invt_cleaned['applt_seq_nr'] > 0) & 
        (df_appl_invt_cleaned['psn_sector_predicted'] == 'NON_INDIVIDUAL')
    ].copy()
    df_app_non_indiv_counts = (
        app_non_indiv_data.groupby(['docdb_family_id', 'person_ctry_code'])
        .agg({'nb_applicants': 'max'})
        .reset_index()
        .rename(columns={'nb_applicants': 'app_non_indiv_count'})
    )


    app_indiv_data = df_appl_invt_cleaned[
        (df_appl_invt_cleaned['applt_seq_nr'] > 0) & 
        (df_appl_invt_cleaned['psn_sector_predicted'] == 'INDIVIDUAL')
    ].copy()
    df_app_indiv_counts = (
        app_indiv_data.groupby(['docdb_family_id', 'person_ctry_code'])
        .agg({'nb_applicants': 'max'})
        .reset_index()
        .rename(columns={'nb_applicants': 'app_indiv_count'})
    )


    # Color mapping
    all_countries = pd.concat([
        df_inv_indiv_counts['person_ctry_code'],
        df_inv_non_indiv_counts['person_ctry_code'],
        df_app_non_indiv_counts['person_ctry_code'],
        df_app_indiv_counts['person_ctry_code']
    ]).unique()
    all_countries.sort()
    colors = plt.cm.tab20.colors
    if len(all_countries) > len(colors):
        extra_colors = plt.cm.tab20b.colors
        colors = list(colors) + list(extra_colors[:len(all_countries) - len(colors)])
    color_map = {country: colors[i] for i, country in enumerate(all_countries)}
    color_map['Others'] = 'gray'


    # Pivot tables
    inv_indiv_pivot = df_inv_indiv_counts.pivot(index='docdb_family_id', columns='person_ctry_code', values='inv_indiv_count').fillna(0)
    inv_non_indiv_pivot = df_inv_non_indiv_counts.pivot(index='docdb_family_id', columns='person_ctry_code', values='inv_non_indiv_count').fillna(0)
    app_non_indiv_pivot = df_app_non_indiv_counts.pivot(index='docdb_family_id', columns='person_ctry_code', values='app_non_indiv_count').fillna(0)
    app_indiv_pivot = df_app_indiv_counts.pivot(index='docdb_family_id', columns='person_ctry_code', values='app_indiv_count').fillna(0)


    # Ensure consistent index
    all_families = inv_indiv_pivot.index.union(inv_non_indiv_pivot.index).union(app_non_indiv_pivot.index).union(app_indiv_pivot.index)
    inv_indiv_pivot = inv_indiv_pivot.reindex(all_families, fill_value=0)
    inv_non_indiv_pivot = inv_non_indiv_pivot.reindex(all_families, fill_value=0)
    app_non_indiv_pivot = app_non_indiv_pivot.reindex(all_families, fill_value=0)
    app_indiv_pivot = app_indiv_pivot.reindex(all_families, fill_value=0)


    # Sort by total 'sort_by_country' counts
    total_counts = (
        inv_indiv_pivot.get(sort_by_country, pd.Series(0, index=inv_indiv_pivot.index)) +
        inv_non_indiv_pivot.get(sort_by_country, pd.Series(0, index=inv_non_indiv_pivot.index)) +
        app_non_indiv_pivot.get(sort_by_country, pd.Series(0, index=app_non_indiv_pivot.index)) +
        app_indiv_pivot.get(sort_by_country, pd.Series(0, index=app_indiv_pivot.index))
    )
    sort_order = total_counts.sort_values(ascending=False).index
    inv_indiv_pivot = inv_indiv_pivot.loc[sort_order]
    inv_non_indiv_pivot = inv_non_indiv_pivot.loc[sort_order]
    app_non_indiv_pivot = app_non_indiv_pivot.loc[sort_order]
    app_indiv_pivot = app_indiv_pivot.loc[sort_order]


    # Plotting
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    bar_width = 0.4
    index = np.arange(len(inv_indiv_pivot))


    # Positive Left (Inventors - Individuals)
    bottom_inv_indiv = np.zeros(len(index))
    if sort_by_country in inv_indiv_pivot.columns:
        ax.bar(index, inv_indiv_pivot[sort_by_country], bar_width, bottom=bottom_inv_indiv, label=sort_by_country, color=color_map[sort_by_country])
        bottom_inv_indiv += inv_indiv_pivot[sort_by_country]
    for country in inv_indiv_pivot.columns:
        if country != sort_by_country and inv_indiv_pivot[country].sum() > 0:
            ax.bar(index, inv_indiv_pivot[country], bar_width, bottom=bottom_inv_indiv, label=country, color=color_map[country])
            bottom_inv_indiv += inv_indiv_pivot[country]


    # Negative Left (Inventors - Non-Individuals)
    bottom_inv_non_indiv = np.zeros(len(index))
    if sort_by_country in inv_non_indiv_pivot.columns:
        ax.bar(index, -inv_non_indiv_pivot[sort_by_country], bar_width, bottom=bottom_inv_non_indiv, label=sort_by_country if sort_by_country not in inv_indiv_pivot.columns else None, color=color_map[sort_by_country])
        bottom_inv_non_indiv -= inv_non_indiv_pivot[sort_by_country]
    for country in inv_non_indiv_pivot.columns:
        if country != sort_by_country and inv_non_indiv_pivot[country].sum() > 0:
            already_labeled = country in inv_indiv_pivot.columns and inv_indiv_pivot[country].sum() > 0
            ax.bar(index, -inv_non_indiv_pivot[country], bar_width, bottom=bottom_inv_non_indiv, label=country if not already_labeled else None, color=color_map[country])
            bottom_inv_non_indiv -= inv_non_indiv_pivot[country]


    # Positive Right (Applicants - Non-Individuals)
    bottom_app_non_indiv = np.zeros(len(index))
    if sort_by_country in app_non_indiv_pivot.columns:
        ax.bar(index + bar_width, app_non_indiv_pivot[sort_by_country], bar_width, bottom=bottom_app_non_indiv, label=sort_by_country if sort_by_country not in inv_indiv_pivot.columns else None, color=color_map[sort_by_country])
        bottom_app_non_indiv += app_non_indiv_pivot[sort_by_country]
    for country in app_non_indiv_pivot.columns:
        if country != sort_by_country and app_non_indiv_pivot[country].sum() > 0:
            already_labeled = country in inv_indiv_pivot.columns and inv_indiv_pivot[country].sum() > 0
            ax.bar(index + bar_width, app_non_indiv_pivot[country], bar_width, bottom=bottom_app_non_indiv, label=country if not already_labeled else None, color=color_map[country])
            bottom_app_non_indiv += app_non_indiv_pivot[country]


    # Negative Right (Applicants - Individuals)
    bottom_app_indiv = np.zeros(len(index))
    if sort_by_country in app_indiv_pivot.columns:
        ax.bar(index + bar_width, -app_indiv_pivot[sort_by_country], bar_width, bottom=bottom_app_indiv, label=sort_by_country if sort_by_country not in inv_indiv_pivot.columns else None, color=color_map[sort_by_country])
        bottom_app_indiv -= app_indiv_pivot[sort_by_country]
    for country in app_indiv_pivot.columns:
        if country != sort_by_country and app_indiv_pivot[country].sum() > 0:
            already_labeled = country in inv_indiv_pivot.columns and inv_indiv_pivot[country].sum() > 0
            ax.bar(index + bar_width, -app_indiv_pivot[country], bar_width, bottom=bottom_app_indiv, label=country if not already_labeled else None, color=color_map[country])
            bottom_app_indiv -= app_indiv_pivot[country]


    # Customize the plot
    ax.set_title('Inventors and Applicants by Type and Country per docdb_family_id', fontsize=14)
    ax.set_xlabel('Inventors | Applicants', fontsize=12)
    ax.set_ylabel('Count (Positive: Indiv Inv / Non-Indiv App, Negative: Non-Indiv Inv / Indiv App)', fontsize=12)
    tick_positions = index + bar_width / 2
    tick_labels = [str(i+1) for i in range(len(inv_indiv_pivot))]
    ax.set_xticks(tick_positions)
    ax.set_xticklabels(tick_labels, rotation=45, ha='right', fontsize=10)
    ax.legend(title="Country", bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10)
    ax.grid(axis='y', linestyle='--', alpha=0.7)


    # Set y-axis limits
    max_positive = max(bottom_inv_indiv.max(), bottom_app_non_indiv.max())
    max_negative = min(bottom_inv_non_indiv.min(), bottom_app_indiv.min())
    max_height = max(max_positive, abs(max_negative))
    y_offset = max_height * 0.2
    ax.set_ylim(max_negative - y_offset, max_height + y_offset)


    plt.tight_layout()


    # Save plot
    plots_dir = output_dir / 'plots' / 'inventors_applicants_plots'  # Full path relative to output_dir
    plots_dir.mkdir(exist_ok=True, parents=True)  # Create the full directory structure


    # Save the plot
    filename = plots_dir / f"inventor_applicant_indiv_non_indiv_bar_plot_sorted_by_{sort_by_country}_{config.start_year}_{config.end_year}.png"
    plt.savefig(filename, format='png', dpi=dpi, bbox_inches='tight')
    print(f"Saved indiv/non-indiv plot as {filename}")
    plt.close()


    # Return plotted pivot tables with 1-based index
    inv_indiv_pivot_plot = inv_indiv_pivot.reset_index(drop=True)
    inv_indiv_pivot_plot.index += 1
    inv_non_indiv_pivot_plot = inv_non_indiv_pivot.reset_index(drop=True)
    inv_non_indiv_pivot_plot.index += 1
    app_non_indiv_pivot_plot = app_non_indiv_pivot.reset_index(drop=True)
    app_non_indiv_pivot_plot.index += 1
    app_indiv_pivot_plot = app_indiv_pivot.reset_index(drop=True)
    app_indiv_pivot_plot.index += 1


    return {
        'inv_indiv': inv_indiv_pivot_plot,
        'inv_non_indiv': inv_non_indiv_pivot_plot,
        'app_non_indiv': app_non_indiv_pivot_plot,
        'app_indiv': app_indiv_pivot_plot
    }
    
# --- Parent Function ---
def plot_applicants_inventors_details(df_appl_invt, df_applicant_ratios, df_inventor_ratios, df_combined_ratios):
    '''
    Plot stacked bar charts for ratios and counts, returning all plotted data.


    Parameters:
    - df_appl_invt: DataFrame with applicant and inventor details
    - df_applicant_ratios: DataFrame with applicant ratio data
    - df_inventor_ratios: DataFrame with inventor ratio data
    - df_combined_ratios: DataFrame with combined ratio data


    Returns:
    - dict: Contains plotted data for 'applicant_ratio', 'inventor_ratio', 'combined_ratio',
            'inventor_count', 'applicant_count', 'combined_count'
    '''
    plotted_data = {}


    # Plot Ratios
    plotted_data['applicant_ratio'] = plot_ratio_data(df_applicant_ratios, 'applicant', output_dir)
    plotted_data['inventor_ratio'] = plot_ratio_data(df_inventor_ratios, 'inventor', output_dir)
    plotted_data['combined_ratio'] = plot_ratio_data(df_combined_ratios, 'combined', output_dir)


    # Clean and prepare count data
    df_appl_invt['person_ctry_code'] = df_appl_invt['person_ctry_code'].astype(str).str.strip()
    df_appl_invt_cleaned = df_appl_invt[
        df_appl_invt['person_ctry_code'].notna() &
        (df_appl_invt['person_ctry_code'] != '') &
        (df_appl_invt['person_ctry_code'] != ' ') &
        (df_appl_invt['person_ctry_code'].str.len() > 0)
    ].copy()


    # Inventor Counts
    inventor_data = df_appl_invt_cleaned[df_appl_invt_cleaned['invt_seq_nr'] > 0].copy()
    df_inventor_counts = (
        inventor_data.groupby(['docdb_family_id', 'person_ctry_code'])
        .agg({'nb_inventors': 'max'})
        .reset_index()
        .rename(columns={'nb_inventors': 'inventor_count'})
    )
    df_inventor_counts = df_inventor_counts[
        df_inventor_counts['person_ctry_code'].notna() & 
        (df_inventor_counts['person_ctry_code'] != '')
    ]


    # Applicant Counts
    applicant_data = df_appl_invt_cleaned[df_appl_invt_cleaned['applt_seq_nr'] > 0].copy()
    df_applicant_counts = (
        applicant_data.groupby(['docdb_family_id', 'person_ctry_code'])
        .agg({'nb_applicants': 'max'})
        .reset_index()
        .rename(columns={'nb_applicants': 'applicant_count'})
    )
    df_applicant_counts = df_applicant_counts[
        df_applicant_counts['person_ctry_code'].notna() & 
        (df_applicant_counts['person_ctry_code'] != '')
    ]


    # Combined Counts
    df_combined_counts = (
        pd.concat([
            df_inventor_counts[['docdb_family_id', 'person_ctry_code', 'inventor_count']].rename(columns={'inventor_count': 'combined_count'}),
            df_applicant_counts[['docdb_family_id', 'person_ctry_code', 'applicant_count']].rename(columns={'applicant_count': 'combined_count'})
        ])
        .groupby(['docdb_family_id', 'person_ctry_code'])
        .sum()
        .reset_index()
    )
    df_combined_counts = df_combined_counts[
        df_combined_counts['person_ctry_code'].notna() & 
        (df_combined_counts['person_ctry_code'] != '')
    ]


    # Plot Counts
    plotted_data['inventor_count'] = plot_count_data(df_inventor_counts, 'inventor', output_dir)
    plotted_data['applicant_count'] = plot_count_data(df_applicant_counts, 'applicant', output_dir)
    plotted_data['combined_count'] = plot_count_data(df_combined_counts, 'combined', output_dir)


    # Side-by-side plot
    side_by_side_data = plot_inventor_applicant_side_by_side(df_inventor_counts, df_applicant_counts, output_dir)
    plotted_data['side_by_side_inventor'] = side_by_side_data['inventor']
    plotted_data['side_by_side_applicant'] = side_by_side_data['applicant']
    
    # Positive/negative plot for individual/non-individual
    indiv_non_indiv_data = plot_inventor_applicant_indiv_non_indiv(df_appl_invt_cleaned, output_dir)
    plotted_data['inv_indiv'] = indiv_non_indiv_data['inv_indiv']
    plotted_data['inv_non_indiv'] = indiv_non_indiv_data['inv_non_indiv']
    plotted_data['app_non_indiv'] = indiv_non_indiv_data['app_non_indiv']
    plotted_data['app_indiv'] = indiv_non_indiv_data['app_indiv']


    return plotted_data
