import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from pathlib import Path
import logging
from typing import Optional
from typing import Union
import config

# Initialize logger
logger = logging.getLogger(__name__)


############### USINING PLOtly graph for intercation
import plotly.graph_objects as go
def plot_appl_inv_ratios_interactive(
    df_applicant_ratios: pd.DataFrame,
    df_inventor_ratios: pd.DataFrame,
    df_combined_ratios: pd.DataFrame,
    sort_by_country: str = "NO",
    max_legend_countries: int = 10,
) -> dict:
    """
    Generate interactive stacked bar charts using Plotly for applicant, inventor, and combined ratios.

    Parameters:
        df_applicant_ratios (pd.DataFrame): DataFrame with applicant ratio data
        df_inventor_ratios (pd.DataFrame): DataFrame with inventor ratio data
        df_combined_ratios (pd.DataFrame): DataFrame with combined ratio data
        sort_by_country (str): Country code to sort the families by (default 'NO')
        max_legend_countries (int): Maximum number of countries in the legend (default 10)

    Returns:
        dict: Dictionary of Plotly figures keyed by ratio type ('applicant', 'inventor', 'combined')
    """
    # Output directory setup (optional, if saving is still desired)
    base_output_dir = Path(config.Config.output_dir)
    plot_output_dir = base_output_dir / "plots" / "applicants_inventors"
    plot_output_dir.mkdir(parents=True, exist_ok=True)

    # List of DataFrames and their corresponding ratio types
    ratio_data = [
        (df_applicant_ratios, "applicant"),
        (df_inventor_ratios, "inventor"),
        (df_combined_ratios, "combined"),
    ]

    # Store figures for return
    figures = {}

    for df_final, ratio_type in ratio_data:
        if df_final.empty:
            logger.warning(f"No data to plot for {ratio_type} ratios")
            continue

        # Create pivot table and calculate percentages
        pivot_table = df_final.pivot(
            index="docdb_family_id",
            columns="person_ctry_code",
            values=f"{ratio_type}_ratio",
        ).fillna(0)
        percentage_table = pivot_table.div(pivot_table.sum(axis=1), axis=0) * 100

        # Sort by mean contribution across families
        country_order = percentage_table.mean().sort_values(ascending=False).index
        percentage_table = percentage_table[country_order]

        # Sort by the specified country if present
        if sort_by_country in percentage_table.columns:
            percentage_table = percentage_table.sort_values(
                by=sort_by_country, ascending=False
            )
        else:
            logger.warning(f"'{sort_by_country}' not found; sorting by top country.")
            percentage_table = percentage_table.sort_values(
                by=country_order[0], ascending=False
            )

        # Aggregate less significant countries into 'Others'
        if len(percentage_table.columns) > max_legend_countries:
            top_countries = percentage_table.columns[:max_legend_countries]
            others_countries = percentage_table.columns[max_legend_countries:]
            percentage_table["Others"] = percentage_table[others_countries].sum(axis=1)
            percentage_table = percentage_table.drop(columns=others_countries)
        else:
            top_countries = percentage_table.columns

        # Reset index for plotting (1-based index)
        percentage_table = percentage_table.reset_index(drop=True)
        percentage_table.index += 1

        # Create Plotly figure
        fig = go.Figure()

        # Add stacked bars
        for country in percentage_table.columns:
            fig.add_trace(
                go.Bar(
                    x=percentage_table.index.astype(str),
                    y=percentage_table[country],
                    name=country,
                    text=percentage_table[country].round(1).astype(str) + "%",
                    textposition="inside",
                    hoverinfo="x+y+name",
                )
            )

        # Update layout for stacking and styling
        fig.update_layout(
            barmode="stack",
            title=f"{ratio_type.capitalize()} Ratio Contribution by Country",
            xaxis_title=f"Document Family Index (Sorted by '{sort_by_country}')",
            yaxis_title="Percentage Contribution (%)",
            yaxis=dict(range=[0, max(100, percentage_table.sum(axis=1).max() * 1.1)]),
            legend_title="Country",
            legend=dict(x=1.05, y=1, xanchor="left", yanchor="top"),
            template="plotly_white",
        )

        # Store the figure
        figures[ratio_type] = fig

        # Optional: Save as HTML for standalone use
        filename = (
            plot_output_dir
            / f"{ratio_type}_ratio_stacked_bar_plot_sorted_by_{sort_by_country}.html"
        )
        fig.write_html(filename)
        logger.info(f"Saved interactive plot as {filename}")

    return figures


############ END PLOYTLY

def plot_appl_inv_ratios(
    df_applicant_ratios: pd.DataFrame,
    df_inventor_ratios: pd.DataFrame,
    df_combined_ratios: pd.DataFrame,
    sort_by_country: str = "NO",
    output_dir: Path = None,  # Default to None, will use config.output_dir
    figsize: tuple = (12, 8),
    dpi: int = 300,
) -> None:
    """
    Plot stacked bar charts of country ratios for applicants, inventors, and combined for each docdb_family_id.

    Parameters:
        df_applicant_ratios (pd.DataFrame): DataFrame with applicant ratio data
        df_inventor_ratios (pd.DataFrame): DataFrame with inventor ratio data
        df_combined_ratios (pd.DataFrame): DataFrame with combined ratio data
        sort_by_country (str): Country code to sort the families by (default 'NO')
        output_dir (Path, optional): Directory to save the plots; defaults to config.output_dir/plots/applicants_inventors
        figsize (tuple): Figure size (width, height) in inches (default (12, 8))
        dpi (int): Resolution of the saved plot (default 300)
    """
    # Use config.output_dir
    base_output_dir = Path(config.Config.output_dir)
    plot_output_dir = base_output_dir / "plots" / "applicants_inventors"

    # List of DataFrames and their corresponding ratio types
    ratio_data = [
        (df_applicant_ratios, "applicant"),
        (df_inventor_ratios, "inventor"),
        (df_combined_ratios, "combined"),
    ]

    # Maximum number of countries to show in the legend
    MAX_COUNTRIES_IN_LEGEND = 10

    # Ensure output directory exists
    plot_output_dir.mkdir(parents=True, exist_ok=True)

    # Loop over each DataFrame and ratio type
    for df_final, ratio_type in ratio_data:
        if df_final.empty:
            logger.warning(f"No data to plot for {ratio_type} ratios")
            continue
        # Create pivot table and calculate percentages
        pivot_table = df_final.pivot(
            index="docdb_family_id",
            columns="person_ctry_code",
            values=f"{ratio_type}_ratio",
        ).fillna(0)
        percentage_table = pivot_table.div(pivot_table.sum(axis=1), axis=0) * 100

        # Sort by mean contribution across families
        country_order = percentage_table.mean().sort_values(ascending=False).index
        percentage_table = percentage_table[country_order]

        # Sort by the specified country if present
        if sort_by_country in percentage_table.columns:
            percentage_table = percentage_table.sort_values(
                by=sort_by_country, ascending=False
            )

        # Aggregate less significant countries into 'Others'
        if len(percentage_table.columns) > MAX_COUNTRIES_IN_LEGEND:
            top_countries = percentage_table.columns[:MAX_COUNTRIES_IN_LEGEND]
            others_countries = percentage_table.columns[MAX_COUNTRIES_IN_LEGEND:]
            percentage_table["Others"] = percentage_table[others_countries].sum(axis=1)
            percentage_table = percentage_table.drop(columns=others_countries)
        else:
            top_countries = percentage_table.columns

        # Reset index for plotting (1-based index)
        percentage_table = percentage_table.reset_index(drop=True)
        percentage_table.index += 1

        # Plotting
        fig, ax = plt.subplots(figsize=figsize)
        bottom = pd.Series(0, index=percentage_table.index)
        colors = plt.cm.tab20c.colors  # Larger colormap for more unique colors

        for i, country in enumerate(percentage_table.columns):
            ax.bar(
                percentage_table.index.astype(str),
                percentage_table[country],
                bottom=bottom,
                label=(
                    country if country in top_countries or country == "Others" else None
                ),
                color=colors[i % len(colors)],
            )
            bottom = bottom + percentage_table[country]

        # Customize the plot
        ax.set_title(
            f"{ratio_type.capitalize()} Ratio Contribution by Country", fontsize=14
        )
        ax.set_xlabel(
            f"Document Family Index (Sorted by '{sort_by_country}')", fontsize=12
        )
        ax.set_ylabel("Percentage Contribution (%)", fontsize=12)
        ax.set_xticks(percentage_table.index)
        ax.set_xticklabels(percentage_table.index, fontsize=10)
        ax.legend(
            title="Country", bbox_to_anchor=(1.05, 1), loc="upper left", fontsize=10
        )
        ax.set_ylim(0, 120)  # 100% + 20% offset

        plt.tight_layout()

        # Save plot
        filename = (
            plot_output_dir
            / f"{ratio_type}_ratio_stacked_bar_plot_sorted_by_{sort_by_country}.png"
        )
        plt.savefig(filename, format="png", dpi=dpi, bbox_inches="tight")
        logger.info(f"Saved plot as {filename}")
        plt.close()


def plot_appl_inv_counts(
    df_applicant_counts: pd.DataFrame,
    df_inventor_counts: pd.DataFrame,
    df_combined_counts: pd.DataFrame,
    sort_by_country: str = "NO",
    output_dir: Path = None,
    figsize: tuple = (12, 8),
    dpi: int = 300,
) -> None:
    # Use config.output_dir if output_dir is not provided
    base_output_dir = (
        output_dir if output_dir is not None else Path(config.Config.output_dir)
    )
    plot_output_dir = base_output_dir / "plots" / "applicants_inventors"

    # List of DataFrames and their corresponding count types
    count_data = [
        (df_applicant_counts, "applicant"),
        (df_inventor_counts, "inventor"),
        (df_combined_counts, "combined"),
    ]

    # Maximum number of countries to show in the legend
    MAX_COUNTRIES_IN_LEGEND = 10

    # Ensure output directory exists
    plot_output_dir.mkdir(parents=True, exist_ok=True)

    # Define consistent color mapping
    all_countries = pd.concat(
        [
            df_inventor_counts["person_ctry_code"],
            df_applicant_counts["person_ctry_code"],
            df_combined_counts["person_ctry_code"],
        ]
    ).unique()
    all_countries.sort()
    colors = plt.cm.tab20.colors
    if len(all_countries) > len(colors):
        extra_colors = plt.cm.tab20b.colors
        colors = list(colors) + list(extra_colors[: len(all_countries) - len(colors)])
    color_map = {country: colors[i] for i, country in enumerate(all_countries)}
    color_map["Others"] = "gray"

    # Loop over each DataFrame and count type
    for df_final, count_type in count_data:
        if df_final.empty:
            logger.warning(f"No data to plot for {count_type} counts")
            continue

        # Pivot table to get counts per docdb_family_id and person_ctry_code
        pivot_table = df_final.pivot(
            index="docdb_family_id",
            columns="person_ctry_code",
            values=f"{count_type}_count",
        ).fillna(0)

        # Sort by 'sort_by_country' counts if it exists, otherwise by index
        if sort_by_country in pivot_table.columns:
            pivot_table = pivot_table.sort_values(by=sort_by_country, ascending=False)
        else:
            pivot_table = pivot_table.sort_index()

        # Aggregate less significant countries into 'Others'
        if len(pivot_table.columns) > MAX_COUNTRIES_IN_LEGEND:
            country_totals = pivot_table.sum()
            non_zero_countries = country_totals[country_totals > 0].index

            # Always include 'sort_by_country' in top_countries if it has non-zero count
            if sort_by_country in non_zero_countries:
                top_countries = [sort_by_country]
                remaining_countries = non_zero_countries.difference([sort_by_country])
                top_remaining = remaining_countries[: MAX_COUNTRIES_IN_LEGEND - 1]
                top_countries.extend(top_remaining)
            else:
                top_countries = non_zero_countries[:MAX_COUNTRIES_IN_LEGEND]

            others_countries = non_zero_countries.difference(top_countries)
            if others_countries.any():
                pivot_table["Others"] = pivot_table[others_countries].sum(axis=1)
            else:
                pivot_table["Others"] = 0
            pivot_table = pivot_table.drop(columns=others_countries)
        else:
            top_countries = pivot_table.columns

        # Reset index for plotting (1-based index)
        pivot_table = pivot_table.reset_index(drop=True)
        pivot_table.index += 1
        indices = pivot_table.index  # Integer indices (1, 2, 3, ...)

        # Plotting
        fig, ax = plt.subplots(figsize=figsize)
        bottom = pd.Series(0, index=indices)

        # Plot 'sort_by_country' first to make it the bottom bar
        if sort_by_country in pivot_table.columns:
            country_sum = pivot_table[sort_by_country].sum()
            if country_sum > 0:
                ax.bar(
                    indices,
                    pivot_table[sort_by_country],
                    bottom=bottom,
                    label=sort_by_country,
                    color=color_map[sort_by_country],
                )
                bottom = bottom + pivot_table[sort_by_country]

        # Plot remaining countries
        for country in pivot_table.columns:
            if (
                country != sort_by_country
            ):  # Skip 'sort_by_country' since it's already plotted
                country_sum = pivot_table[country].sum()
                if country_sum > 0:
                    ax.bar(
                        indices,
                        pivot_table[country],
                        bottom=bottom,
                        label=(
                            country
                            if country in top_countries or country == "Others"
                            else None
                        ),
                        color=color_map[country],
                    )
                    bottom = bottom + pivot_table[country]

        # Customize the plot
        ax.set_title(
            f"{count_type.capitalize()} Count by Country for Each docdb_family_id",
            fontsize=14,
        )
        ax.set_xlabel(
            f"Document Family Index (Sorted by '{sort_by_country}')", fontsize=12
        )
        ax.set_ylabel(f"Number of {count_type.capitalize()}s", fontsize=12)
        ax.set_xticks(indices)
        ax.set_xticklabels(indices, fontsize=10)
        ax.legend(
            title="Country", bbox_to_anchor=(1.05, 1), loc="upper left", fontsize=10
        )

        # Dynamic y-axis limit with 20% headroom
        max_height = bottom.max()
        ax.set_ylim(0, max_height * 1.2 if max_height > 0 else 10)

        plt.tight_layout()

        # Save plot
        filename = (
            plot_output_dir
            / f"{count_type}_count_stacked_bar_plot_sorted_by_{sort_by_country}.png"
        )
        plt.savefig(filename, format="png", dpi=dpi, bbox_inches="tight")
        logger.info(f"Saved plot as {filename}")
        plt.close()


def plot_appl_inv_side_by_side(
    df_applicant_counts: pd.DataFrame,
    df_inventor_counts: pd.DataFrame,
    sort_by_country: str = "NO",
    output_dir: Path = None,
    figsize: tuple = (12, 8),
    dpi: int = 300,
) -> None:
    """
    Plot side-by-side bar charts of inventor and applicant counts per country for each docdb_family_id.

    Parameters:
        df_applicant_counts (pd.DataFrame): DataFrame with applicant count data (columns: docdb_family_id, person_ctry_code, applicant_count)
        df_inventor_counts (pd.DataFrame): DataFrame with inventor count data (columns: docdb_family_id, person_ctry_code, inventor_count)
        sort_by_country (str): Country code to sort the families by (default 'NO')
        output_dir (Path, optional): Directory to save the plots; defaults to config.output_dir/plots/applicants_inventors
        figsize (tuple): Figure size (width, height) in inches (default (12, 8))
        dpi (int): Resolution of the saved plot (default 300)
    """
    # Use config.output_dir if output_dir is not provided
    base_output_dir = (
        output_dir if output_dir is not None else Path(config.Config.output_dir)
    )
    plot_output_dir = base_output_dir / "plots" / "applicants_inventors"

    # Ensure output directory exists
    plot_output_dir.mkdir(parents=True, exist_ok=True)

    # Check for empty data
    if df_applicant_counts.empty and df_inventor_counts.empty:
        logger.warning("No data to plot for inventor and applicant counts")
        return

    # Define consistent color mapping
    all_countries = pd.concat(
        [
            df_inventor_counts["person_ctry_code"],
            df_applicant_counts["person_ctry_code"],
        ]
    ).unique()
    all_countries.sort()
    colors = plt.cm.tab20.colors
    if len(all_countries) > len(colors):
        extra_colors = plt.cm.tab20b.colors
        colors = list(colors) + list(extra_colors[: len(all_countries) - len(colors)])
    color_map = {country: colors[i] for i, country in enumerate(all_countries)}
    color_map["Others"] = "gray"

    # Pivot tables for inventors and applicants
    inventor_pivot = df_inventor_counts.pivot(
        index="docdb_family_id", columns="person_ctry_code", values="inventor_count"
    ).fillna(0)
    applicant_pivot = df_applicant_counts.pivot(
        index="docdb_family_id", columns="person_ctry_code", values="applicant_count"
    ).fillna(0)

    # Ensure both pivots have the same index
    all_families = inventor_pivot.index.union(applicant_pivot.index)
    inventor_pivot = inventor_pivot.reindex(all_families, fill_value=0)
    applicant_pivot = applicant_pivot.reindex(all_families, fill_value=0)

    # Sort by total 'sort_by_country' counts (inventors + applicants)
    if (
        sort_by_country in inventor_pivot.columns
        or sort_by_country in applicant_pivot.columns
    ):
        no_inventors = inventor_pivot.get(
            sort_by_country, pd.Series(0, index=inventor_pivot.index)
        )
        no_applicants = applicant_pivot.get(
            sort_by_country, pd.Series(0, index=applicant_pivot.index)
        )
        total_no_counts = no_inventors + no_applicants
        sort_order = total_no_counts.sort_values(ascending=False).index
        inventor_pivot = inventor_pivot.loc[sort_order]
        applicant_pivot = applicant_pivot.loc[sort_order]

    # Reset index for plotting (1-based index)
    inventor_pivot = inventor_pivot.reset_index(drop=True)
    applicant_pivot = applicant_pivot.reset_index(drop=True)
    inventor_pivot.index += 1
    applicant_pivot.index += 1
    index = np.arange(len(inventor_pivot))

    # Plotting
    fig, ax = plt.subplots(figsize=figsize)
    bar_width = 0.4

    # Track which countries have been labeled to avoid duplicates in legend
    labeled_countries = set()

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
                label=(
                    sort_by_country
                    if sort_by_country not in labeled_countries
                    else None
                ),
                color=color_map[sort_by_country],
            )
            bottom_inv += inventor_pivot[sort_by_country]
            labeled_countries.add(sort_by_country)
    for country in inventor_pivot.columns:
        if country != sort_by_country:
            country_sum = inventor_pivot[country].sum()
            if country_sum > 0:
                ax.bar(
                    index,
                    inventor_pivot[country],
                    bar_width,
                    bottom=bottom_inv,
                    label=country if country not in labeled_countries else None,
                    color=color_map[country],
                )
                bottom_inv += inventor_pivot[country]
                labeled_countries.add(country)

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
                label=(
                    sort_by_country
                    if sort_by_country not in labeled_countries
                    else None
                ),
                color=color_map[sort_by_country],
            )
            bottom_app += applicant_pivot[sort_by_country]
            labeled_countries.add(sort_by_country)
    for country in applicant_pivot.columns:
        if country != sort_by_country:
            country_sum = applicant_pivot[country].sum()
            if country_sum > 0:
                ax.bar(
                    index + bar_width,
                    applicant_pivot[country],
                    bar_width,
                    bottom=bottom_app,
                    label=country if country not in labeled_countries else None,
                    color=color_map[country],
                )
                bottom_app += applicant_pivot[country]
                labeled_countries.add(country)

    # Customize the plot
    ax.set_title(
        "Inventors (Left) and Applicants (Right) by Country per docdb_family_id",
        fontsize=14,
    )
    ax.set_xlabel(f"Document Family Index (Sorted by '{sort_by_country}')", fontsize=12)
    ax.set_ylabel("Count", fontsize=12)
    tick_positions = index + bar_width / 2
    tick_labels = [str(i + 1) for i in range(len(inventor_pivot))]
    ax.set_xticks(tick_positions)
    ax.set_xticklabels(tick_labels, rotation=45, ha="right", fontsize=10)
    ax.legend(title="Country", bbox_to_anchor=(1.05, 1), loc="upper left", fontsize=10)
    ax.grid(axis="y", linestyle="--", alpha=0.7)

    # Dynamic y-axis limit with 20% headroom
    max_height_inv = bottom_inv.max()
    max_height_app = bottom_app.max()
    max_height = max(max_height_inv, max_height_app)
    ax.set_ylim(0, max_height * 1.2 if max_height > 0 else 10)

    plt.tight_layout()

    # Save plot
    filename = (
        plot_output_dir
        / f"inventor_applicant_side_by_side_bar_plot_sorted_by_{sort_by_country}.png"
    )
    plt.savefig(filename, format="png", dpi=dpi, bbox_inches="tight")
    logger.info(f"Saved plot as {filename}")
    plt.close()


def plot_appl_inv_indiv_non_indiv(
    df_inv_indiv_counts: pd.DataFrame,
    df_inv_non_indiv_counts: pd.DataFrame,
    df_app_non_indiv_counts: pd.DataFrame,
    df_app_indiv_counts: pd.DataFrame,
    sort_by_country: str = "NO",
    output_dir: Path = None,
    figsize: tuple = (12, 8),
    dpi: int = 300,
) -> None:
    """
    Plot positive and negative bar charts for individual/non-individual inventors and applicants per country for each docdb_family_id.

    Parameters:
        df_inv_indiv_counts (pd.DataFrame): DataFrame with individual inventor counts (columns: docdb_family_id, person_ctry_code, inv_indiv_count)
        df_inv_non_indiv_counts (pd.DataFrame): DataFrame with non-individual inventor counts (columns: docdb_family_id, person_ctry_code, inv_non_indiv_count)
        df_app_non_indiv_counts (pd.DataFrame): DataFrame with non-individual applicant counts (columns: docdb_family_id, person_ctry_code, app_non_indiv_count)
        df_app_indiv_counts (pd.DataFrame): DataFrame with individual applicant counts (columns: docdb_family_id, person_ctry_code, app_indiv_count)
        sort_by_country (str): Country code to sort the families by (default 'NO')
        output_dir (Path, optional): Directory to save the plots; defaults to config.output_dir/plots/applicants_inventors
        figsize (tuple): Figure size (width, height) in inches (default (12, 8))
        dpi (int): Resolution of the saved plot (default 300)
    """
    # Use config.output_dir if output_dir is not provided
    base_output_dir = (
        output_dir if output_dir is not None else Path(config.Config.output_dir)
    )
    plot_output_dir = base_output_dir / "plots" / "applicants_inventors"

    # Ensure output directory exists
    plot_output_dir.mkdir(parents=True, exist_ok=True)

    # Check for empty data
    if all(
        df.empty
        for df in [
            df_inv_indiv_counts,
            df_inv_non_indiv_counts,
            df_app_non_indiv_counts,
            df_app_indiv_counts,
        ]
    ):
        logger.warning("No data to plot for individual/non-individual counts")
        return

    # Define consistent color mapping
    all_countries = pd.concat(
        [
            df_inv_indiv_counts["person_ctry_code"],
            df_inv_non_indiv_counts["person_ctry_code"],
            df_app_non_indiv_counts["person_ctry_code"],
            df_app_indiv_counts["person_ctry_code"],
        ]
    ).unique()
    all_countries.sort()
    colors = plt.cm.tab20.colors
    if len(all_countries) > len(colors):
        extra_colors = plt.cm.tab20b.colors
        colors = list(colors) + list(extra_colors[: len(all_countries) - len(colors)])
    color_map = {country: colors[i] for i, country in enumerate(all_countries)}
    color_map["Others"] = "gray"

    # Pivot tables
    inv_indiv_pivot = df_inv_indiv_counts.pivot(
        index="docdb_family_id", columns="person_ctry_code", values="inv_indiv_count"
    ).fillna(0)
    inv_non_indiv_pivot = df_inv_non_indiv_counts.pivot(
        index="docdb_family_id",
        columns="person_ctry_code",
        values="inv_non_indiv_count",
    ).fillna(0)
    app_non_indiv_pivot = df_app_non_indiv_counts.pivot(
        index="docdb_family_id",
        columns="person_ctry_code",
        values="app_non_indiv_count",
    ).fillna(0)
    app_indiv_pivot = df_app_indiv_counts.pivot(
        index="docdb_family_id", columns="person_ctry_code", values="app_indiv_count"
    ).fillna(0)

    # Ensure all pivots have the same index
    all_families = (
        inv_indiv_pivot.index.union(inv_non_indiv_pivot.index)
        .union(app_non_indiv_pivot.index)
        .union(app_indiv_pivot.index)
    )
    inv_indiv_pivot = inv_indiv_pivot.reindex(all_families, fill_value=0)
    inv_non_indiv_pivot = inv_non_indiv_pivot.reindex(all_families, fill_value=0)
    app_non_indiv_pivot = app_non_indiv_pivot.reindex(all_families, fill_value=0)
    app_indiv_pivot = app_indiv_pivot.reindex(all_families, fill_value=0)

    # Sort by total 'sort_by_country' counts across all categories
    total_sort_counts = (
        inv_indiv_pivot.get(sort_by_country, pd.Series(0, index=inv_indiv_pivot.index))
        + inv_non_indiv_pivot.get(
            sort_by_country, pd.Series(0, index=inv_non_indiv_pivot.index)
        )
        + app_non_indiv_pivot.get(
            sort_by_country, pd.Series(0, index=app_non_indiv_pivot.index)
        )
        + app_indiv_pivot.get(
            sort_by_country, pd.Series(0, index=app_indiv_pivot.index)
        )
    )
    sort_order = total_sort_counts.sort_values(ascending=False).index
    inv_indiv_pivot = inv_indiv_pivot.loc[sort_order]
    inv_non_indiv_pivot = inv_non_indiv_pivot.loc[sort_order]
    app_non_indiv_pivot = app_non_indiv_pivot.loc[sort_order]
    app_indiv_pivot = app_indiv_pivot.loc[sort_order]

    # Reset index for plotting (1-based index)
    inv_indiv_pivot = inv_indiv_pivot.reset_index(drop=True)
    inv_non_indiv_pivot = inv_non_indiv_pivot.reset_index(drop=True)
    app_non_indiv_pivot = app_non_indiv_pivot.reset_index(drop=True)
    app_indiv_pivot = app_indiv_pivot.reset_index(drop=True)
    inv_indiv_pivot.index += 1
    inv_non_indiv_pivot.index += 1
    app_non_indiv_pivot.index += 1
    app_indiv_pivot.index += 1
    index = np.arange(len(inv_indiv_pivot))

    # Plotting
    fig, ax = plt.subplots(figsize=figsize)
    bar_width = 0.4

    # Track labeled countries to avoid duplicates in legend
    labeled_countries = set()

    # Positive Left (Inventors - Individuals)
    bottom_inv_indiv = np.zeros(len(index))
    if sort_by_country in inv_indiv_pivot.columns:
        country_sum = inv_indiv_pivot[sort_by_country].sum()
        if country_sum > 0:
            ax.bar(
                index,
                inv_indiv_pivot[sort_by_country],
                bar_width,
                bottom=bottom_inv_indiv,
                label=(
                    sort_by_country
                    if sort_by_country not in labeled_countries
                    else None
                ),
                color=color_map[sort_by_country],
            )
            bottom_inv_indiv += inv_indiv_pivot[sort_by_country]
            labeled_countries.add(sort_by_country)
    for country in inv_indiv_pivot.columns:
        if country != sort_by_country and inv_indiv_pivot[country].sum() > 0:
            ax.bar(
                index,
                inv_indiv_pivot[country],
                bar_width,
                bottom=bottom_inv_indiv,
                label=country if country not in labeled_countries else None,
                color=color_map[country],
            )
            bottom_inv_indiv += inv_indiv_pivot[country]
            labeled_countries.add(country)

    # Negative Left (Inventors - Non-Individuals)
    bottom_inv_non_indiv = np.zeros(len(index))
    if sort_by_country in inv_non_indiv_pivot.columns:
        country_sum = inv_non_indiv_pivot[sort_by_country].sum()
        if country_sum > 0:
            ax.bar(
                index,
                -inv_non_indiv_pivot[sort_by_country],
                bar_width,
                bottom=bottom_inv_non_indiv,
                label=(
                    sort_by_country
                    if sort_by_country not in labeled_countries
                    else None
                ),
                color=color_map[sort_by_country],
            )
            bottom_inv_non_indiv -= inv_non_indiv_pivot[sort_by_country]
            labeled_countries.add(sort_by_country)
    for country in inv_non_indiv_pivot.columns:
        if country != sort_by_country and inv_non_indiv_pivot[country].sum() > 0:
            ax.bar(
                index,
                -inv_non_indiv_pivot[country],
                bar_width,
                bottom=bottom_inv_non_indiv,
                label=country if country not in labeled_countries else None,
                color=color_map[country],
            )
            bottom_inv_non_indiv -= inv_non_indiv_pivot[country]
            labeled_countries.add(country)

    # Positive Right (Applicants - Non-Individuals)
    bottom_app_non_indiv = np.zeros(len(index))
    if sort_by_country in app_non_indiv_pivot.columns:
        country_sum = app_non_indiv_pivot[sort_by_country].sum()
        if country_sum > 0:
            ax.bar(
                index + bar_width,
                app_non_indiv_pivot[sort_by_country],
                bar_width,
                bottom=bottom_app_non_indiv,
                label=(
                    sort_by_country
                    if sort_by_country not in labeled_countries
                    else None
                ),
                color=color_map[sort_by_country],
            )
            bottom_app_non_indiv += app_non_indiv_pivot[sort_by_country]
            labeled_countries.add(sort_by_country)
    for country in app_non_indiv_pivot.columns:
        if country != sort_by_country and app_non_indiv_pivot[country].sum() > 0:
            ax.bar(
                index + bar_width,
                app_non_indiv_pivot[country],
                bar_width,
                bottom=bottom_app_non_indiv,
                label=country if country not in labeled_countries else None,
                color=color_map[country],
            )
            bottom_app_non_indiv += app_non_indiv_pivot[country]
            labeled_countries.add(country)

    # Negative Right (Applicants - Individuals)
    bottom_app_indiv = np.zeros(len(index))
    if sort_by_country in app_indiv_pivot.columns:
        country_sum = app_indiv_pivot[sort_by_country].sum()
        if country_sum > 0:
            ax.bar(
                index + bar_width,
                -app_indiv_pivot[sort_by_country],
                bar_width,
                bottom=bottom_app_indiv,
                label=(
                    sort_by_country
                    if sort_by_country not in labeled_countries
                    else None
                ),
                color=color_map[sort_by_country],
            )
            bottom_app_indiv -= app_indiv_pivot[sort_by_country]
            labeled_countries.add(sort_by_country)
    for country in app_indiv_pivot.columns:
        if country != sort_by_country and app_indiv_pivot[country].sum() > 0:
            ax.bar(
                index + bar_width,
                -app_indiv_pivot[country],
                bar_width,
                bottom=bottom_app_indiv,
                label=country if country not in labeled_countries else None,
                color=color_map[country],
            )
            bottom_app_indiv -= app_indiv_pivot[country]
            labeled_countries.add(country)

    # Customize the plot
    ax.set_title(
        "Inventors and Applicants by Type and Country per docdb_family_id", fontsize=14
    )
    ax.set_xlabel(f"Document Family Index (Sorted by '{sort_by_country}')", fontsize=12)
    ax.set_ylabel(
        "Count (Positive: Indiv Inv / Non-Indiv App, Negative: Non-Indiv Inv / Indiv App)",
        fontsize=12,
    )
    tick_positions = index + bar_width / 2
    tick_labels = [str(i + 1) for i in range(len(inv_indiv_pivot))]
    ax.set_xticks(tick_positions)
    ax.set_xticklabels(tick_labels, rotation=45, ha="right", fontsize=10)
    ax.legend(title="Country", bbox_to_anchor=(1.05, 1), loc="upper left", fontsize=10)
    ax.grid(axis="y", linestyle="--", alpha=0.7)

    # Set y-axis limits with 20% offset
    max_positive = max(bottom_inv_indiv.max(), bottom_app_non_indiv.max())
    max_negative = min(bottom_inv_non_indiv.min(), bottom_app_indiv.min())
    max_height = max(max_positive, abs(max_negative))
    y_offset = max_height * 0.2 if max_height > 0 else 2  # Default offset if no data
    ax.set_ylim(max_negative - y_offset, max_height + y_offset)

    plt.tight_layout()

    # Save plot
    filename = (
        plot_output_dir
        / f"inventor_applicant_indiv_non_indiv_bar_plot_sorted_by_{sort_by_country}.png"
    )
    plt.savefig(filename, format="png", dpi=dpi, bbox_inches="tight")
    logger.info(f"Saved plot as {filename}")
    plt.close()

    # Add individual applicant ratio  to count ration plot


def plot_individ_appl_inv_ratios(
    df_applicant_ratios: pd.DataFrame,
    df_inventor_ratios: pd.DataFrame,
    df_combined_ratios: pd.DataFrame,
    df_indiv_applicant_ratio: pd.DataFrame,
    sort_by_country: str = "NO",
    output_dir: Path = None,  # Default to None, will use config.output_dir
    figsize: tuple = (12, 8),
    dpi: int = 300,
) -> None:

    base_output_dir = Path(config.Config.output_dir)
    plot_output_dir = base_output_dir / "plots" / "applicants_inventors"

    # List of DataFrames and their corresponding ratio types
    ratio_data = [
        (df_applicant_ratios, "applicant"),
        (df_inventor_ratios, "inventor"),
        (df_combined_ratios, "combined"),
        (df_indiv_applicant_ratio, "indiv_applicant"),  # Added new DataFrame
    ]

    # Maximum number of countries to show in the legend
    MAX_COUNTRIES_IN_LEGEND = 10

    # Ensure output directory exists
    plot_output_dir.mkdir(parents=True, exist_ok=True)

    # Loop over each DataFrame and ratio type
    for df_final, ratio_type in ratio_data:
        if df_final.empty:
            logger.warning(f"No data to plot for {ratio_type} ratios")
            continue

        if ratio_type == "indiv_applicant":
            # Pivot table for individual applicant ratio
            pivot_table = df_final.pivot(
                index="docdb_family_id",
                columns="person_ctry_code",
                values="indiv_applicant_ratio",
            ).fillna(
                0
            )  # Fill NaN with 0 for plotting consistency

            # Sort by specified country if present
            if sort_by_country in pivot_table.columns:
                # Filter out families where specified country's ratio is NaN
                pivot_table_filtered = pivot_table[pivot_table[sort_by_country].notna()]
                # Sort by specified country's ratio
                pivot_table_sorted = pivot_table_filtered.sort_values(
                    by=sort_by_country, ascending=False
                )
            else:
                pivot_table_sorted = pivot_table
                logger.warning(
                    f"Specified country '{sort_by_country}' not found in data"
                )

            # Determine top countries based on mean ratio
            mean_ratios = pivot_table_sorted.mean().sort_values(ascending=False)
            top_countries = mean_ratios.index[:MAX_COUNTRIES_IN_LEGEND]

            # Include specified country if not in top N
            if (
                sort_by_country not in top_countries
                and sort_by_country in pivot_table_sorted.columns
            ):
                top_countries = top_countries.append(pd.Index([sort_by_country]))

            # Reset index for plotting (1-based index)
            pivot_table_sorted = pivot_table_sorted.reset_index(drop=True)
            pivot_table_sorted.index += 1

            # Create line plot
            fig, ax = plt.subplots(figsize=figsize)
            for country in top_countries:
                ax.plot(
                    pivot_table_sorted.index.astype(str),
                    pivot_table_sorted[country],
                    label=country,
                    marker="o",  # Small markers to indicate data points
                    alpha=0.7,  # Transparency to handle overlapping lines
                )

            # Customize the plot
            ax.set_title(
                "Individual to Non-Individual Applicant Ratio by Country", fontsize=14
            )
            ax.set_xlabel(
                f"Document Family Index (Sorted by '{sort_by_country}')", fontsize=12
            )
            ax.set_ylabel("Individual to Non-Individual Applicant Ratio", fontsize=12)
            ax.set_xticks(
                pivot_table_sorted.index[::5]
            )  # Show every 5th tick to avoid clutter
            ax.set_xticklabels(pivot_table_sorted.index[::5], fontsize=10, rotation=45)
            ax.legend(
                title="Country", bbox_to_anchor=(1.05, 1), loc="upper left", fontsize=10
            )
            ax.set_ylim(bottom=0)  # Start y-axis at 0
            ax.grid(
                True, linestyle="--", alpha=0.3
            )  # Optional: light grid for readability

            plt.tight_layout()

            # Save plot
            filename = (
                plot_output_dir
                / f"indiv_applicant_ratio_plot_sorted_by_{sort_by_country}.png"
            )
            plt.savefig(filename, format="png", dpi=dpi, bbox_inches="tight")
            logger.info(f"Saved plot as {filename}")
            plt.close()

    else:
        # Existing plotting logic for other ratio types
        pivot_table = df_final.pivot(
            index="docdb_family_id",
            columns="person_ctry_code",
            values=f"{ratio_type}_ratio",
        ).fillna(0)
        percentage_table = pivot_table.div(pivot_table.sum(axis=1), axis=0) * 100

        # Sort by mean contribution across families
        country_order = percentage_table.mean().sort_values(ascending=False).index
        percentage_table = percentage_table[country_order]

        # Sort by the specified country if present
        if sort_by_country in percentage_table.columns:
            percentage_table = percentage_table.sort_values(
                by=sort_by_country, ascending=False
            )

        # Aggregate less significant countries into 'Others'
        if len(percentage_table.columns) > MAX_COUNTRIES_IN_LEGEND:
            top_countries = percentage_table.columns[:MAX_COUNTRIES_IN_LEGEND]
            others_countries = percentage_table.columns[MAX_COUNTRIES_IN_LEGEND:]
            percentage_table["Others"] = percentage_table[others_countries].sum(axis=1)
            percentage_table = percentage_table.drop(columns=others_countries)
        else:
            top_countries = percentage_table.columns

        # Reset index for plotting (1-based index)
        percentage_table = percentage_table.reset_index(drop=True)
        percentage_table.index += 1

        # Plotting
        fig, ax = plt.subplots(figsize=figsize)
        bottom = pd.Series(0, index=percentage_table.index)
        colors = plt.cm.tab20c.colors

        for i, country in enumerate(percentage_table.columns):
            ax.bar(
                percentage_table.index.astype(str),
                percentage_table[country],
                bottom=bottom,
                label=(
                    country if country in top_countries or country == "Others" else None
                ),
                color=colors[i % len(colors)],
            )
            bottom = bottom + percentage_table[country]

        # Customize the plot
        ax.set_title(
            f"{ratio_type.capitalize()} Ratio Contribution by Country", fontsize=14
        )
        ax.set_xlabel(
            f"Document Family Index (Sorted by '{sort_by_country}')", fontsize=12
        )
        ax.set_ylabel("Percentage Contribution (%)", fontsize=12)
        ax.set_xticks(percentage_table.index)
        ax.set_xticklabels(percentage_table.index, fontsize=10)
        ax.legend(
            title="Country", bbox_to_anchor=(1.05, 1), loc="upper left", fontsize=10
        )
        ax.set_ylim(0, 120)

        plt.tight_layout()

        # Save plot
        filename = (
            plot_output_dir
            / f"{ratio_type}_individ_applicant_ratio_stacked_bar_plot_sorted_by_{sort_by_country}.png"
        )
        plt.savefig(filename, format="png", dpi=dpi, bbox_inches="tight")
        logger.info(f"Saved plot as {filename}")
        plt.close()
