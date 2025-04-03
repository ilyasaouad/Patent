## Working plot codes:
# For plot def get_applicants_inventors_data in get_applicants_inventors_details.py
#######  Ploting ratios  procentage % of inventors ###############
##################################################################
def get_applicants_inventors_data(country_code: str, start_year: int, end_year: int):
    if len(country_code) != 2 or not country_code.isalpha():
        raise ValueError("Country code must be a 2-letter string (e.g., 'NO').")
    if start_year < 1900 or start_year > 2025:
        raise ValueError("Start year must be between 1900 and 2023.")
    if end_year < start_year or end_year > 2023:
        raise ValueError(
            "End year must be greater than or equal to start year and <= 2023."
        )

    country_code = country_code
    start_year = start_year
    end_year = end_year

    df_unique_family_ids = get_family_ids(country_code, start_year, end_year)

    df_unique_family_ids = df_unique_family_ids[
        0:5
    ]  # for testing purposes ################## Testing ####################
    # Make sure df_unique_family_ids is a list
    family_ids_list = df_unique_family_ids.tolist()

    print(f"df_unique_family_ids: {df_unique_family_ids.shape[0]}")

    # For testing purposes
    # df_unique_family_ids = [69137772, 69143432] #, 74181202, 74505320]
    # family_ids_list = df_unique_family_ids

    # Get applicant and inventor
    df_appl_invt = get_applicant_inventor(family_ids_list)

    # Aggerate names and appln_ids into same rows
    df_appl_invt_agg = aggregate_applicants_inventors(df_appl_invt)

    # Get ration of inventors only, applicant only, and in combinationcountry par application
    (df_applicant_ratios, df_inventor_ratios, df_combined_ratios) = (
        calculate_applicant_inventor_ratios(df_appl_invt)
    )

    ## Working plot codes:


# For plot def get_applicants_inventors_data in get_applicants_inventors_details.py
#######  Ploting ratios  procentage % of inventors ###############
##################################################################
def get_applicants_inventors_data(country_code: str, start_year: int, end_year: int):
    if len(country_code) != 2 or not country_code.isalpha():
        raise ValueError("Country code must be a 2-letter string (e.g., 'NO').")
    if start_year < 1900 or start_year > 2025:
        raise ValueError("Start year must be between 1900 and 2023.")
    if end_year < start_year or end_year > 2023:
        raise ValueError(
            "End year must be greater than or equal to start year and <= 2023."
        )

    country_code = country_code
    start_year = start_year
    end_year = end_year

    df_unique_family_ids = get_family_ids(country_code, start_year, end_year)

    df_unique_family_ids = df_unique_family_ids[
        0:5
    ]  # for testing purposes ################## Testing ####################
    # Make sure df_unique_family_ids is a list
    family_ids_list = df_unique_family_ids.tolist()

    print(f"df_unique_family_ids: {df_unique_family_ids.shape[0]}")

    # For testing purposes
    # df_unique_family_ids = [69137772, 69143432] #, 74181202, 74505320]
    # family_ids_list = df_unique_family_ids

    # Get applicant and inventor
    df_appl_invt = get_applicant_inventor(family_ids_list)

    # Aggerate names and appln_ids into same rows
    df_appl_invt_agg = aggregate_applicants_inventors(df_appl_invt)

    # Get ration of inventors only, applicant only, and in combinationcountry par application
    (df_applicant_ratios, df_inventor_ratios, df_combined_ratios) = (
        calculate_applicant_inventor_ratios(df_appl_invt)
    )

    ###################### PLOTing #################################
    """
    Plot a stacked bar chart of country ratios for each docdb_family_id.

    Parameters:
    - df: DataFrame with ratio data (e.g., df_applicant_ratios, df_inventor_ratios, or df_combined_ratios)
    - ratio_type: str, one of 'applicant', 'inventor', or 'combined' to determine the column name and title
    - sort_by_country: str, country code to sort the families by (default 'NO')
    - figsize: tuple, figure size (width, height) in inches
    - dpi: int, resolution of the saved plot
    """
    # List of DataFrames and their corresponding ratio types
    ratio_data = [
        (df_applicant_ratios, "applicant"),
        (df_inventor_ratios, "inventor"),
        (df_combined_ratios, "combined"),
    ]

    # Maximum number of countries to show in the legend
    MAX_COUNTRIES_IN_LEGEND = 10

    # Loop over each DataFrame and ratio type
    for df_final, ratio_type in ratio_data:
        pivot_table = df_final.pivot(
            index="docdb_family_id",
            columns="person_ctry_code",
            values=f"{ratio_type}_ratio",
        ).fillna(0)
        percentage_table = pivot_table.div(pivot_table.sum(axis=1), axis=0) * 100
        country_order = percentage_table.mean().sort_values(ascending=False).index
        percentage_table = percentage_table[country_order]
        if country_code in percentage_table.columns:
            percentage_table = percentage_table.sort_values(
                by=country_code, ascending=False
            )

        if len(percentage_table.columns) > MAX_COUNTRIES_IN_LEGEND:
            top_countries = percentage_table.columns[:MAX_COUNTRIES_IN_LEGEND]
            others_countries = percentage_table.columns[MAX_COUNTRIES_IN_LEGEND:]
            percentage_table["Others"] = percentage_table[others_countries].sum(axis=1)
            percentage_table = percentage_table.drop(columns=others_countries)
        else:
            top_countries = percentage_table.columns

        percentage_table = percentage_table.reset_index(drop=True)
        percentage_table.index += 1

        # Plotting
        fig, ax = plt.subplots(figsize=(12, 8))  # Use ax for consistency
        bottom = pd.Series(0, index=percentage_table.index)
        colors = plt.cm.tab20.colors

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
            f"{ratio_type.capitalize()} Ratio Contribution by Country for Each docdb_family_id",
            fontsize=14,
        )
        ax.set_xlabel(
            f"Document Family Index (Sorted by '{config.country_code}')", fontsize=12
        )
        ax.set_ylabel("Percentage Contribution (%)", fontsize=12)
        ax.set_xticks(percentage_table.index)
        ax.set_xticklabels(percentage_table.index, fontsize=10)
        ax.legend(
            title="Country", bbox_to_anchor=(1.05, 1), loc="upper left", fontsize=10
        )

        # Add 20% offset (since it’s percentages, max is 100, so offset is 20)
        ax.set_ylim(0, 100 + 20)  # 100% + 20%

        plt.tight_layout()

        # Save plot
        output_dir = Path("output_plots")
        output_dir.mkdir(exist_ok=True)
        filename = (
            output_dir
            / f"{ratio_type}_ratio_stacked_bar_plot_sorted_by_{config.country_code}_{config.start_year}_{config.end_year}.png"
        )
        plt.savefig(filename, format="png", dpi=300, bbox_inches="tight")
        print(f"Saved plot as {filename}")
        plt.close()

    ################################################
    ####### Count of inventors per country per family
    #################################################

    # Step 1: Remove rows with empty or whitespace-only person_ctry_code
    # Convert to string and strip whitespace/special characters, then filter
    df_appl_invt["person_ctry_code"] = (
        df_appl_invt["person_ctry_code"].astype(str).str.strip()
    )
    df_appl_invt_cleaned = df_appl_invt[
        df_appl_invt["person_ctry_code"].notna()  # Remove NaN
        & (df_appl_invt["person_ctry_code"] != "")  # Remove empty string
        & (df_appl_invt["person_ctry_code"] != " ")  # Remove single space
        & (
            df_appl_invt["person_ctry_code"].str.len() > 0
        )  # Ensure length > 0 after stripping
    ].copy()

    # Step 2: Inventor Counts
    inventor_data = df_appl_invt_cleaned[df_appl_invt_cleaned["invt_seq_nr"] > 0].copy()
    df_inventor_counts = (
        inventor_data.groupby(["docdb_family_id", "person_ctry_code"])
        .agg({"nb_inventors": "max"})
        .reset_index()
        .rename(columns={"nb_inventors": "inventor_count"})
    )
    # Double-check for empty codes
    df_inventor_counts = df_inventor_counts[
        df_inventor_counts["person_ctry_code"].notna()
        & (df_inventor_counts["person_ctry_code"] != "")
    ]

    # Step 3: Applicant Counts
    applicant_data = df_appl_invt_cleaned[
        df_appl_invt_cleaned["applt_seq_nr"] > 0
    ].copy()
    df_applicant_counts = (
        applicant_data.groupby(["docdb_family_id", "person_ctry_code"])
        .agg({"nb_applicants": "max"})
        .reset_index()
        .rename(columns={"nb_applicants": "applicant_count"})
    )
    # Double-check for empty codes
    df_applicant_counts = df_applicant_counts[
        df_applicant_counts["person_ctry_code"].notna()
        & (df_applicant_counts["person_ctry_code"] != "")
    ]

    # Step 4: Combined Counts
    df_combined_counts = (
        pd.concat(
            [
                df_inventor_counts[
                    ["docdb_family_id", "person_ctry_code", "inventor_count"]
                ].rename(columns={"inventor_count": "combined_count"}),
                df_applicant_counts[
                    ["docdb_family_id", "person_ctry_code", "applicant_count"]
                ].rename(columns={"applicant_count": "combined_count"}),
            ]
        )
        .groupby(["docdb_family_id", "person_ctry_code"])
        .sum()
        .reset_index()
    )
    # Final check for empty codes
    df_combined_counts = df_combined_counts[
        df_combined_counts["person_ctry_code"].notna()
        & (df_combined_counts["person_ctry_code"] != "")
    ]

    # Print results with debug info
    print("Inventor Counts:")
    print(df_inventor_counts)
    print("\nApplicant Counts:")
    print(df_applicant_counts)
    print("\nCombined Counts:")
    print(df_combined_counts)
    print("\nUnique person_ctry_code values in df_combined_counts:")
    print(df_combined_counts["person_ctry_code"].unique())

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

    # Plotting function with 'NO' at bottom and sorted by 'NO' counts
    def plot_stacked_bar_chart_counts(
        df, count_type, sort_by_country="NO", figsize=(12, 8), dpi=300
    ):
        if df.empty:
            print(f"No data to plot for {count_type} counts.")
            return

        # Pivot table to get counts per docdb_family_id and person_ctry_code
        pivot_table = df.pivot(
            index="docdb_family_id",
            columns="person_ctry_code",
            values=f"{count_type}_count",
        ).fillna(0)

        # Sort by 'NO' counts if 'NO' exists, otherwise by index
        if sort_by_country in pivot_table.columns:
            pivot_table = pivot_table.sort_values(by=sort_by_country, ascending=False)
        else:
            pivot_table = pivot_table.sort_index()

        # Handle legend: limit to top 10 countries, group others
        MAX_COUNTRIES_IN_LEGEND = 10
        country_totals = pivot_table.sum()
        non_zero_countries = country_totals[country_totals > 0].index
        if len(non_zero_countries) > MAX_COUNTRIES_IN_LEGEND:
            top_countries = non_zero_countries[:MAX_COUNTRIES_IN_LEGEND]
            others_countries = non_zero_countries[MAX_COUNTRIES_IN_LEGEND:]
            pivot_table["Others"] = pivot_table[others_countries].sum(axis=1)
            pivot_table = pivot_table.drop(columns=others_countries)
        else:
            top_countries = non_zero_countries

        # Reset index for plotting
        pivot_table = pivot_table.reset_index(drop=True)
        pivot_table.index += 1  # Start index at 1
        indices = pivot_table.index  # Integer indices (1, 2, 3, ...)

        # Create the plot
        plt.figure(figsize=figsize)
        bottom = pd.Series(0, index=indices)

        # Plot 'NO' first to make it the bottom bar
        if sort_by_country in pivot_table.columns:
            country_sum = pivot_table[sort_by_country].sum()
            if country_sum > 0:
                plt.bar(
                    indices,
                    pivot_table[sort_by_country],
                    bottom=bottom,
                    label=sort_by_country if sort_by_country in top_countries else None,
                    color=color_map[sort_by_country],
                )
                bottom = bottom + pivot_table[sort_by_country]

        # Plot remaining countries
        for country in pivot_table.columns:
            if country != sort_by_country:  # Skip 'NO' since it's already plotted
                country_sum = pivot_table[country].sum()
                if country_sum > 0:
                    plt.bar(
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

        # Customize plot with integer x-axis ticks
        plt.title(
            f"{count_type.capitalize()} Count by Country for Each docdb_family_id",
            fontsize=14,
        )
        plt.xlabel(
            f"Document Family Index (Sorted by '{sort_by_country}' {count_type.capitalize()}s)",
            fontsize=12,
        )
        plt.ylabel(f"Number of {count_type.capitalize()}s", fontsize=12)
        plt.xticks(ticks=indices, labels=indices, fontsize=10)
        plt.legend(
            title="Country", bbox_to_anchor=(1.05, 1), loc="upper left", fontsize=10
        )
        plt.tight_layout()

        # Save plot
        output_dir = Path("output_plots")
        output_dir.mkdir(exist_ok=True)
        filename = (
            output_dir
            / f"{count_type}_count_stacked_bar_plot_sorted_by_{sort_by_country}.png"
        )
        plt.savefig(filename, format="png", dpi=dpi, bbox_inches="tight")
        print(f"Saved plot as {filename}")
        plt.close()

    # Generate the plots
    plot_stacked_bar_chart_counts(df_inventor_counts, "inventor", sort_by_country="NO")
    plot_stacked_bar_chart_counts(
        df_applicant_counts, "applicant", sort_by_country="NO"
    )
    plot_stacked_bar_chart_counts(df_combined_counts, "combined", sort_by_country="NO")

    ###################################################################
    # Inventor counts and Applicat counts in same plot side by side bar
    ###################################################################
    # Step 1: Remove rows with empty or whitespace-only person_ctry_code
    df_appl_invt["person_ctry_code"] = (
        df_appl_invt["person_ctry_code"].astype(str).str.strip()
    )
    df_appl_invt_cleaned = df_appl_invt[
        df_appl_invt["person_ctry_code"].notna()  # Remove NaN
        & (df_appl_invt["person_ctry_code"] != "")  # Remove empty string
        & (df_appl_invt["person_ctry_code"] != " ")  # Remove single space
        & (
            df_appl_invt["person_ctry_code"].str.len() > 0
        )  # Ensure length > 0 after stripping
    ].copy()

    # Step 2: Inventor Counts
    inventor_data = df_appl_invt_cleaned[df_appl_invt_cleaned["invt_seq_nr"] > 0].copy()
    df_inventor_counts = (
        inventor_data.groupby(["docdb_family_id", "person_ctry_code"])
        .agg({"nb_inventors": "max"})
        .reset_index()
        .rename(columns={"nb_inventors": "inventor_count"})
    )
    df_inventor_counts = df_inventor_counts[
        df_inventor_counts["person_ctry_code"].notna()
        & (df_inventor_counts["person_ctry_code"] != "")
    ]

    # Step 3: Applicant Counts
    applicant_data = df_appl_invt_cleaned[
        df_appl_invt_cleaned["applt_seq_nr"] > 0
    ].copy()
    df_applicant_counts = (
        applicant_data.groupby(["docdb_family_id", "person_ctry_code"])
        .agg({"nb_applicants": "max"})
        .reset_index()
        .rename(columns={"nb_applicants": "applicant_count"})
    )
    df_applicant_counts = df_applicant_counts[
        df_applicant_counts["person_ctry_code"].notna()
        & (df_applicant_counts["person_ctry_code"] != "")
    ]

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

    # Sort by total 'NO' counts (inventors + applicants)
    sort_country = "NO"
    if (
        sort_country in inventor_pivot.columns
        or sort_country in applicant_pivot.columns
    ):
        no_inventors = inventor_pivot.get(
            sort_country, pd.Series(0, index=inventor_pivot.index)
        )
        no_applicants = applicant_pivot.get(
            sort_country, pd.Series(0, index=applicant_pivot.index)
        )
        total_no_counts = no_inventors + no_applicants
        sort_order = total_no_counts.sort_values(ascending=False).index
        inventor_pivot = inventor_pivot.loc[sort_order]
        applicant_pivot = applicant_pivot.loc[sort_order]

    # Plotting
    fig, ax = plt.subplots(figsize=(12, 8), dpi=300)
    bar_width = 0.4
    index = np.arange(len(inventor_pivot))

    # Plot inventor bars (left)
    bottom_inv = np.zeros(len(index))
    if sort_country in inventor_pivot.columns:
        country_sum = inventor_pivot[sort_country].sum()
        if country_sum > 0:
            ax.bar(
                index,
                inventor_pivot[sort_country],
                bar_width,
                bottom=bottom_inv,
                label=sort_country,
                color=color_map[sort_country],
            )
            bottom_inv += inventor_pivot[sort_country]
    for country in inventor_pivot.columns:
        if country != sort_country:
            country_sum = inventor_pivot[country].sum()
            if country_sum > 0:
                ax.bar(
                    index,
                    inventor_pivot[country],
                    bar_width,
                    bottom=bottom_inv,
                    label=(
                        country
                        if country_sum > 0 and country not in [sort_country]
                        else None
                    ),
                    color=color_map[country],
                )
                bottom_inv += inventor_pivot[country]

    # Plot applicant bars (right)
    bottom_app = np.zeros(len(index))
    if sort_country in applicant_pivot.columns:
        country_sum = applicant_pivot[sort_country].sum()
        if country_sum > 0:
            ax.bar(
                index + bar_width,
                applicant_pivot[sort_country],
                bar_width,
                bottom=bottom_app,
                label=(
                    sort_country if sort_country not in inventor_pivot.columns else None
                ),
                color=color_map[sort_country],
            )
            bottom_app += applicant_pivot[sort_country]
    for country in applicant_pivot.columns:
        if country != sort_country:
            country_sum = applicant_pivot[country].sum()
            if country_sum > 0:
                already_labeled = (
                    country in inventor_pivot.columns
                    and inventor_pivot[country].sum() > 0
                )
                ax.bar(
                    index + bar_width,
                    applicant_pivot[country],
                    bar_width,
                    bottom=bottom_app,
                    label=country if not already_labeled else None,
                    color=color_map[country],
                )
                bottom_app += applicant_pivot[country]

    # Customize the plot
    ax.set_title(
        "Inventors (Left) and Applicants (Right) by Country per docdb_family_id",
        fontsize=14,
    )
    ax.set_xlabel("Inventors | Applicants", fontsize=12)
    ax.set_ylabel("Count", fontsize=12)
    tick_positions = index + bar_width / 2
    tick_labels = [str(i + 1) for i in range(len(inv_indiv_pivot))]
    ax.set_xticks(tick_positions)
    ax.set_xticklabels(tick_labels, rotation=45, ha="right", fontsize=10)
    ax.legend(title="Country", bbox_to_anchor=(1.05, 1), loc="upper left", fontsize=10)
    ax.grid(axis="y", linestyle="--", alpha=0.7)

    # Add offset to y-axis limit (3 units above the tallest bar)
    max_height_inv = bottom_inv.max()
    max_height_app = bottom_app.max()
    max_height = max(max_height_inv, max_height_app)
    ax.set_ylim(0, max_height + 3)  # Offset of 3 units

    plt.tight_layout()

    # Save plot
    output_dir = Path("output_plots")
    output_dir.mkdir(exist_ok=True)
    filename = output_dir / "inventor_applicant_side_by_side_bar_plot.png"
    plt.savefig(filename, format="png", dpi=300, bbox_inches="tight")
    print(f"Saved plot as {filename}")
    plt.close()

    #######################################################
    # Positiv and negative plot for inventors and applicants
    ########################################################
    import pandas as pd
    import matplotlib.pyplot as plt
    import numpy as np
    from pathlib import Path
    import re
    from typing import Optional

    # Classification function with PATSTAT psn_sector values
    def classify_entity(name: str, psn_sector: Optional[str] = None) -> str:
        """
        Classify a name as 'INDIVIDUAL' or 'NON_INDIVIDUAL' based on psn_sector or naming patterns.

        Args:
            name (str): The entity name (e.g., from person_name or psn_name).
            psn_sector (Optional[str]): Existing sector value, if available.

        Returns:
            str: 'INDIVIDUAL' or 'NON_INDIVIDUAL'.
        """
        # Define all expected PATSTAT psn_sector categories
        valid_sectors = {
            "INDIVIDUAL": "INDIVIDUAL",
            "COMPANY": "NON_INDIVIDUAL",
            "UNIVERSITY": "NON_INDIVIDUAL",
            "GOV NON-PROFIT": "NON_INDIVIDUAL",
            "GOVERNMENT": "NON_INDIVIDUAL",
            "HOSPITAL": "NON_INDIVIDUAL",
            "UNKNOWN": None,  # Trigger prediction for 'UNKNOWN'
            "": None,  # Trigger prediction for empty string
        }

        # If psn_sector is provided and in valid_sectors (not None), use it
        if (
            psn_sector
            and psn_sector.strip() in valid_sectors
            and valid_sectors[psn_sector.strip()] is not None
        ):
            return valid_sectors[psn_sector.strip()]

        # Predict based on name for missing, empty, 'UNKNOWN', or invalid psn_sector
        name = name.strip().upper()
        non_indiv_keywords = [
            "AS",
            "ASA",
            "INC",
            "LTD",
            "LLC",
            "CORP",
            "COMPANY",
            "TECHNOLOGIES",
            "TECH",
            "UNIVERSITY",
            "INSTITUTE",
            "GROUP",
            "INDUSTRY",
            "NORWAY",
            "SCANDINAVIA",
        ]
        if any(keyword in name for keyword in non_indiv_keywords):
            return "NON_INDIVIDUAL"

        parts = re.split(r"[,\s]+", name)
        if ("," in name or len(parts) >= 2) and not any(
            part in non_indiv_keywords for part in parts
        ):
            if any(len(part) <= 2 for part in parts) or len(parts) <= 4:
                return "INDIVIDUAL"

        return "NON_INDIVIDUAL"

    # Step 1: Clean and classify
    df_appl_invt["person_ctry_code"] = (
        df_appl_invt["person_ctry_code"].astype(str).str.strip()
    )
    df_appl_invt_cleaned = df_appl_invt[
        df_appl_invt["person_ctry_code"].notna()
        & (df_appl_invt["person_ctry_code"] != "")
        & (df_appl_invt["person_ctry_code"] != " ")
        & (df_appl_invt["person_ctry_code"].str.len() > 0)
    ].copy()

    # Apply classification using PATSTAT psn_sector values
    df_appl_invt_cleaned["psn_sector_predicted"] = df_appl_invt_cleaned.apply(
        lambda row: classify_entity(row["person_name"], row["psn_sector"]), axis=1
    )

    # Step 2: Categorize Inventors and Applicants
    # Inventors who are individuals
    inv_indiv_data = df_appl_invt_cleaned[
        (df_appl_invt_cleaned["invt_seq_nr"] > 0)
        & (df_appl_invt_cleaned["psn_sector_predicted"] == "INDIVIDUAL")
    ].copy()
    df_inv_indiv_counts = (
        inv_indiv_data.groupby(["docdb_family_id", "person_ctry_code"])
        .agg({"nb_inventors": "max"})
        .reset_index()
        .rename(columns={"nb_inventors": "inv_indiv_count"})
    )

    # Inventors who are not individuals
    inv_non_indiv_data = df_appl_invt_cleaned[
        (df_appl_invt_cleaned["invt_seq_nr"] > 0)
        & (df_appl_invt_cleaned["psn_sector_predicted"] == "NON_INDIVIDUAL")
    ].copy()
    df_inv_non_indiv_counts = (
        inv_non_indiv_data.groupby(["docdb_family_id", "person_ctry_code"])
        .agg({"nb_inventors": "max"})
        .reset_index()
        .rename(columns={"nb_inventors": "inv_non_indiv_count"})
    )

    # Applicants who are not individuals
    app_non_indiv_data = df_appl_invt_cleaned[
        (df_appl_invt_cleaned["applt_seq_nr"] > 0)
        & (df_appl_invt_cleaned["psn_sector_predicted"] == "NON_INDIVIDUAL")
    ].copy()
    df_app_non_indiv_counts = (
        app_non_indiv_data.groupby(["docdb_family_id", "person_ctry_code"])
        .agg({"nb_applicants": "max"})
        .reset_index()
        .rename(columns={"nb_applicants": "app_non_indiv_count"})
    )

    # Applicants who are individuals
    app_indiv_data = df_appl_invt_cleaned[
        (df_appl_invt_cleaned["applt_seq_nr"] > 0)
        & (df_appl_invt_cleaned["psn_sector_predicted"] == "INDIVIDUAL")
    ].copy()
    df_app_indiv_counts = (
        app_indiv_data.groupby(["docdb_family_id", "person_ctry_code"])
        .agg({"nb_applicants": "max"})
        .reset_index()
        .rename(columns={"nb_applicants": "app_indiv_count"})
    )

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

    # Sort by total 'NO' counts across all categories
    sort_country = "NO"
    total_no_counts = (
        inv_indiv_pivot.get(sort_country, pd.Series(0, index=inv_indiv_pivot.index))
        + inv_non_indiv_pivot.get(
            sort_country, pd.Series(0, index=inv_non_indiv_pivot.index)
        )
        + app_non_indiv_pivot.get(
            sort_country, pd.Series(0, index=app_non_indiv_pivot.index)
        )
        + app_indiv_pivot.get(sort_country, pd.Series(0, index=app_indiv_pivot.index))
    )
    sort_order = total_no_counts.sort_values(ascending=False).index
    inv_indiv_pivot = inv_indiv_pivot.loc[sort_order]
    inv_non_indiv_pivot = inv_non_indiv_pivot.loc[sort_order]
    app_non_indiv_pivot = app_non_indiv_pivot.loc[sort_order]
    app_indiv_pivot = app_indiv_pivot.loc[sort_order]

    # Plotting
    fig, ax = plt.subplots(figsize=(12, 8), dpi=300)
    bar_width = 0.4
    index = np.arange(len(inv_indiv_pivot))

    # Positive Left (Inventors - Individuals)
    bottom_inv_indiv = np.zeros(len(index))
    if sort_country in inv_indiv_pivot.columns:
        ax.bar(
            index,
            inv_indiv_pivot[sort_country],
            bar_width,
            bottom=bottom_inv_indiv,
            label=sort_country,
            color=color_map[sort_country],
        )
        bottom_inv_indiv += inv_indiv_pivot[sort_country]
    for country in inv_indiv_pivot.columns:
        if country != sort_country and inv_indiv_pivot[country].sum() > 0:
            ax.bar(
                index,
                inv_indiv_pivot[country],
                bar_width,
                bottom=bottom_inv_indiv,
                label=country,
                color=color_map[country],
            )
            bottom_inv_indiv += inv_indiv_pivot[country]

    # Negative Left (Inventors - Non-Individuals)
    bottom_inv_non_indiv = np.zeros(len(index))
    if sort_country in inv_non_indiv_pivot.columns:
        ax.bar(
            index,
            -inv_non_indiv_pivot[sort_country],
            bar_width,
            bottom=bottom_inv_non_indiv,
            label=sort_country if sort_country not in inv_indiv_pivot.columns else None,
            color=color_map[sort_country],
        )
        bottom_inv_non_indiv -= inv_non_indiv_pivot[sort_country]
    for country in inv_non_indiv_pivot.columns:
        if country != sort_country and inv_non_indiv_pivot[country].sum() > 0:
            already_labeled = (
                country in inv_indiv_pivot.columns
                and inv_indiv_pivot[country].sum() > 0
            )
            ax.bar(
                index,
                -inv_non_indiv_pivot[country],
                bar_width,
                bottom=bottom_inv_non_indiv,
                label=country if not already_labeled else None,
                color=color_map[country],
            )
            bottom_inv_non_indiv -= inv_non_indiv_pivot[country]

    # Positive Right (Applicants - Non-Individuals)
    bottom_app_non_indiv = np.zeros(len(index))
    if sort_country in app_non_indiv_pivot.columns:
        ax.bar(
            index + bar_width,
            app_non_indiv_pivot[sort_country],
            bar_width,
            bottom=bottom_app_non_indiv,
            label=sort_country if sort_country not in inv_indiv_pivot.columns else None,
            color=color_map[sort_country],
        )
        bottom_app_non_indiv += app_non_indiv_pivot[sort_country]
    for country in app_non_indiv_pivot.columns:
        if country != sort_country and app_non_indiv_pivot[country].sum() > 0:
            already_labeled = (
                country in inv_indiv_pivot.columns
                and inv_indiv_pivot[country].sum() > 0
            )
            ax.bar(
                index + bar_width,
                app_non_indiv_pivot[country],
                bar_width,
                bottom=bottom_app_non_indiv,
                label=country if not already_labeled else None,
                color=color_map[country],
            )
            bottom_app_non_indiv += app_non_indiv_pivot[country]

    # Negative Right (Applicants - Individuals)
    bottom_app_indiv = np.zeros(len(index))
    if sort_country in app_indiv_pivot.columns:
        ax.bar(
            index + bar_width,
            -app_indiv_pivot[sort_country],
            bar_width,
            bottom=bottom_app_indiv,
            label=sort_country if sort_country not in inv_indiv_pivot.columns else None,
            color=color_map[sort_country],
        )
        bottom_app_indiv -= app_indiv_pivot[sort_country]
    for country in app_indiv_pivot.columns:
        if country != sort_country and app_indiv_pivot[country].sum() > 0:
            already_labeled = (
                country in inv_indiv_pivot.columns
                and inv_indiv_pivot[country].sum() > 0
            )
            ax.bar(
                index + bar_width,
                -app_indiv_pivot[country],
                bar_width,
                bottom=bottom_app_indiv,
                label=country if not already_labeled else None,
                color=color_map[country],
            )
            bottom_app_indiv -= app_indiv_pivot[country]

    # Customize the plot
    ax.set_title(
        "Inventors and Applicants by Type and Country per docdb_family_id", fontsize=14
    )
    ax.set_xlabel("Inventors | Applicants", fontsize=12)
    ax.set_ylabel(
        "Count (Positive: Indiv Inv / Non-Indiv App, Negative: Non-Indiv Inv / Indiv App)",
        fontsize=12,
    )
    tick_positions = index + bar_width / 2
    tick_labels = [
        str(i + 1) for i in range(len(inv_indiv_pivot))
    ]  # Updated as per your previous request
    ax.set_xticks(tick_positions)
    ax.set_xticklabels(tick_labels, rotation=45, ha="right", fontsize=10)
    ax.legend(title="Country", bbox_to_anchor=(1.05, 1), loc="upper left", fontsize=10)
    ax.grid(axis="y", linestyle="--", alpha=0.7)

    # Set y-axis limits with 20% offset
    max_positive = max(bottom_inv_indiv.max(), bottom_app_non_indiv.max())
    max_negative = min(bottom_inv_non_indiv.min(), bottom_app_indiv.min())
    max_height = max(max_positive, abs(max_negative))
    y_offset = max_height * 0.2
    ax.set_ylim(max_negative - y_offset, max_height + y_offset)

    plt.tight_layout()

    # Save plot
    output_dir = Path("output_plots")
    output_dir.mkdir(exist_ok=True)
    filename = output_dir / "inventor_applicant_indiv_non_indiv_bar_plot.png"
    plt.savefig(filename, format="png", dpi=300, bbox_inches="tight")
    print(f"Saved plot as {filename}")
    plt.close()

    ################################################
    ####### Count of inventors per country per family
    #################################################

    # Step 1: Remove rows with empty or whitespace-only person_ctry_code
    # Convert to string and strip whitespace/special characters, then filter
    df_appl_invt["person_ctry_code"] = (
        df_appl_invt["person_ctry_code"].astype(str).str.strip()
    )
    df_appl_invt_cleaned = df_appl_invt[
        df_appl_invt["person_ctry_code"].notna()  # Remove NaN
        & (df_appl_invt["person_ctry_code"] != "")  # Remove empty string
        & (df_appl_invt["person_ctry_code"] != " ")  # Remove single space
        & (
            df_appl_invt["person_ctry_code"].str.len() > 0
        )  # Ensure length > 0 after stripping
    ].copy()

    # Step 2: Inventor Counts
    inventor_data = df_appl_invt_cleaned[df_appl_invt_cleaned["invt_seq_nr"] > 0].copy()
    df_inventor_counts = (
        inventor_data.groupby(["docdb_family_id", "person_ctry_code"])
        .agg({"nb_inventors": "max"})
        .reset_index()
        .rename(columns={"nb_inventors": "inventor_count"})
    )
    # Double-check for empty codes
    df_inventor_counts = df_inventor_counts[
        df_inventor_counts["person_ctry_code"].notna()
        & (df_inventor_counts["person_ctry_code"] != "")
    ]

    # Step 3: Applicant Counts
    applicant_data = df_appl_invt_cleaned[
        df_appl_invt_cleaned["applt_seq_nr"] > 0
    ].copy()
    df_applicant_counts = (
        applicant_data.groupby(["docdb_family_id", "person_ctry_code"])
        .agg({"nb_applicants": "max"})
        .reset_index()
        .rename(columns={"nb_applicants": "applicant_count"})
    )
    # Double-check for empty codes
    df_applicant_counts = df_applicant_counts[
        df_applicant_counts["person_ctry_code"].notna()
        & (df_applicant_counts["person_ctry_code"] != "")
    ]

    # Step 4: Combined Counts
    df_combined_counts = (
        pd.concat(
            [
                df_inventor_counts[
                    ["docdb_family_id", "person_ctry_code", "inventor_count"]
                ].rename(columns={"inventor_count": "combined_count"}),
                df_applicant_counts[
                    ["docdb_family_id", "person_ctry_code", "applicant_count"]
                ].rename(columns={"applicant_count": "combined_count"}),
            ]
        )
        .groupby(["docdb_family_id", "person_ctry_code"])
        .sum()
        .reset_index()
    )
    # Final check for empty codes
    df_combined_counts = df_combined_counts[
        df_combined_counts["person_ctry_code"].notna()
        & (df_combined_counts["person_ctry_code"] != "")
    ]

    # Print results with debug info
    print("Inventor Counts:")
    print(df_inventor_counts)
    print("\nApplicant Counts:")
    print(df_applicant_counts)
    print("\nCombined Counts:")
    print(df_combined_counts)
    print("\nUnique person_ctry_code values in df_combined_counts:")
    print(df_combined_counts["person_ctry_code"].unique())

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

    # Plotting function with 'NO' at bottom and sorted by 'NO' counts
    def plot_stacked_bar_chart_counts(
        df, count_type, sort_by_country="NO", figsize=(12, 8), dpi=300
    ):
        if df.empty:
            print(f"No data to plot for {count_type} counts.")
            return

        # Pivot table to get counts per docdb_family_id and person_ctry_code
        pivot_table = df.pivot(
            index="docdb_family_id",
            columns="person_ctry_code",
            values=f"{count_type}_count",
        ).fillna(0)

        # Sort by 'NO' counts if 'NO' exists, otherwise by index
        if sort_by_country in pivot_table.columns:
            pivot_table = pivot_table.sort_values(by=sort_by_country, ascending=False)
        else:
            pivot_table = pivot_table.sort_index()

        # Handle legend: limit to top 10 countries, group others
        MAX_COUNTRIES_IN_LEGEND = 10
        country_totals = pivot_table.sum()
        non_zero_countries = country_totals[country_totals > 0].index
        if len(non_zero_countries) > MAX_COUNTRIES_IN_LEGEND:
            top_countries = non_zero_countries[:MAX_COUNTRIES_IN_LEGEND]
            others_countries = non_zero_countries[MAX_COUNTRIES_IN_LEGEND:]
            pivot_table["Others"] = pivot_table[others_countries].sum(axis=1)
            pivot_table = pivot_table.drop(columns=others_countries)
        else:
            top_countries = non_zero_countries

        # Reset index for plotting
        pivot_table = pivot_table.reset_index(drop=True)
        pivot_table.index += 1  # Start index at 1
        indices = pivot_table.index  # Integer indices (1, 2, 3, ...)

        # Create the plot
        plt.figure(figsize=figsize)
        bottom = pd.Series(0, index=indices)

        # Plot 'NO' first to make it the bottom bar
        if sort_by_country in pivot_table.columns:
            country_sum = pivot_table[sort_by_country].sum()
            if country_sum > 0:
                plt.bar(
                    indices,
                    pivot_table[sort_by_country],
                    bottom=bottom,
                    label=sort_by_country if sort_by_country in top_countries else None,
                    color=color_map[sort_by_country],
                )
                bottom = bottom + pivot_table[sort_by_country]

        # Plot remaining countries
        for country in pivot_table.columns:
            if country != sort_by_country:  # Skip 'NO' since it's already plotted
                country_sum = pivot_table[country].sum()
                if country_sum > 0:
                    plt.bar(
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

        # Customize plot with integer x-axis ticks
        plt.title(
            f"{count_type.capitalize()} Count by Country for Each docdb_family_id",
            fontsize=14,
        )
        plt.xlabel(
            f"Document Family Index (Sorted by '{sort_by_country}' {count_type.capitalize()}s)",
            fontsize=12,
        )
        plt.ylabel(f"Number of {count_type.capitalize()}s", fontsize=12)
        plt.xticks(ticks=indices, labels=indices, fontsize=10)
        plt.legend(
            title="Country", bbox_to_anchor=(1.05, 1), loc="upper left", fontsize=10
        )
        plt.tight_layout()

        # Save plot
        output_dir = Path("output_plots")
        output_dir.mkdir(exist_ok=True)
        filename = (
            output_dir
            / f"{count_type}_count_stacked_bar_plot_sorted_by_{sort_by_country}.png"
        )
        plt.savefig(filename, format="png", dpi=dpi, bbox_inches="tight")
        print(f"Saved plot as {filename}")
        plt.close()

    # Generate the plots
    plot_stacked_bar_chart_counts(df_inventor_counts, "inventor", sort_by_country="NO")
    plot_stacked_bar_chart_counts(
        df_applicant_counts, "applicant", sort_by_country="NO"
    )
    plot_stacked_bar_chart_counts(df_combined_counts, "combined", sort_by_country="NO")

    ###################################################################
    # Inventor counts and Applicat counts in same plot side by side bar
    ###################################################################
    # Step 1: Remove rows with empty or whitespace-only person_ctry_code
    df_appl_invt["person_ctry_code"] = (
        df_appl_invt["person_ctry_code"].astype(str).str.strip()
    )
    df_appl_invt_cleaned = df_appl_invt[
        df_appl_invt["person_ctry_code"].notna()  # Remove NaN
        & (df_appl_invt["person_ctry_code"] != "")  # Remove empty string
        & (df_appl_invt["person_ctry_code"] != " ")  # Remove single space
        & (
            df_appl_invt["person_ctry_code"].str.len() > 0
        )  # Ensure length > 0 after stripping
    ].copy()

    # Step 2: Inventor Counts
    inventor_data = df_appl_invt_cleaned[df_appl_invt_cleaned["invt_seq_nr"] > 0].copy()
    df_inventor_counts = (
        inventor_data.groupby(["docdb_family_id", "person_ctry_code"])
        .agg({"nb_inventors": "max"})
        .reset_index()
        .rename(columns={"nb_inventors": "inventor_count"})
    )
    df_inventor_counts = df_inventor_counts[
        df_inventor_counts["person_ctry_code"].notna()
        & (df_inventor_counts["person_ctry_code"] != "")
    ]

    # Step 3: Applicant Counts
    applicant_data = df_appl_invt_cleaned[
        df_appl_invt_cleaned["applt_seq_nr"] > 0
    ].copy()
    df_applicant_counts = (
        applicant_data.groupby(["docdb_family_id", "person_ctry_code"])
        .agg({"nb_applicants": "max"})
        .reset_index()
        .rename(columns={"nb_applicants": "applicant_count"})
    )
    df_applicant_counts = df_applicant_counts[
        df_applicant_counts["person_ctry_code"].notna()
        & (df_applicant_counts["person_ctry_code"] != "")
    ]

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

    # Sort by total 'NO' counts (inventors + applicants)
    sort_country = "NO"
    if (
        sort_country in inventor_pivot.columns
        or sort_country in applicant_pivot.columns
    ):
        no_inventors = inventor_pivot.get(
            sort_country, pd.Series(0, index=inventor_pivot.index)
        )
        no_applicants = applicant_pivot.get(
            sort_country, pd.Series(0, index=applicant_pivot.index)
        )
        total_no_counts = no_inventors + no_applicants
        sort_order = total_no_counts.sort_values(ascending=False).index
        inventor_pivot = inventor_pivot.loc[sort_order]
        applicant_pivot = applicant_pivot.loc[sort_order]

    # Plotting
    fig, ax = plt.subplots(figsize=(12, 8), dpi=300)
    bar_width = 0.4
    index = np.arange(len(inventor_pivot))

    # Plot inventor bars (left)
    bottom_inv = np.zeros(len(index))
    if sort_country in inventor_pivot.columns:
        country_sum = inventor_pivot[sort_country].sum()
        if country_sum > 0:
            ax.bar(
                index,
                inventor_pivot[sort_country],
                bar_width,
                bottom=bottom_inv,
                label=sort_country,
                color=color_map[sort_country],
            )
            bottom_inv += inventor_pivot[sort_country]
    for country in inventor_pivot.columns:
        if country != sort_country:
            country_sum = inventor_pivot[country].sum()
            if country_sum > 0:
                ax.bar(
                    index,
                    inventor_pivot[country],
                    bar_width,
                    bottom=bottom_inv,
                    label=(
                        country
                        if country_sum > 0 and country not in [sort_country]
                        else None
                    ),
                    color=color_map[country],
                )
                bottom_inv += inventor_pivot[country]

    # Plot applicant bars (right)
    bottom_app = np.zeros(len(index))
    if sort_country in applicant_pivot.columns:
        country_sum = applicant_pivot[sort_country].sum()
        if country_sum > 0:
            ax.bar(
                index + bar_width,
                applicant_pivot[sort_country],
                bar_width,
                bottom=bottom_app,
                label=(
                    sort_country if sort_country not in inventor_pivot.columns else None
                ),
                color=color_map[sort_country],
            )
            bottom_app += applicant_pivot[sort_country]
    for country in applicant_pivot.columns:
        if country != sort_country:
            country_sum = applicant_pivot[country].sum()
            if country_sum > 0:
                already_labeled = (
                    country in inventor_pivot.columns
                    and inventor_pivot[country].sum() > 0
                )
                ax.bar(
                    index + bar_width,
                    applicant_pivot[country],
                    bar_width,
                    bottom=bottom_app,
                    label=country if not already_labeled else None,
                    color=color_map[country],
                )
                bottom_app += applicant_pivot[country]

    # Customize the plot
    ax.set_title(
        "Inventors (Left) and Applicants (Right) by Country per docdb_family_id",
        fontsize=14,
    )
    ax.set_xlabel("Inventors | Applicants", fontsize=12)
    ax.set_ylabel("Count", fontsize=12)
    tick_positions = index + bar_width / 2
    tick_labels = [str(i + 1) for i in range(len(inv_indiv_pivot))]
    ax.set_xticks(tick_positions)
    ax.set_xticklabels(tick_labels, rotation=45, ha="right", fontsize=10)
    ax.legend(title="Country", bbox_to_anchor=(1.05, 1), loc="upper left", fontsize=10)
    ax.grid(axis="y", linestyle="--", alpha=0.7)

    # Add offset to y-axis limit (3 units above the tallest bar)
    max_height_inv = bottom_inv.max()
    max_height_app = bottom_app.max()
    max_height = max(max_height_inv, max_height_app)
    ax.set_ylim(0, max_height + 3)  # Offset of 3 units

    plt.tight_layout()

    # Save plot
    output_dir = Path("output_plots")
    output_dir.mkdir(exist_ok=True)
    filename = output_dir / "inventor_applicant_side_by_side_bar_plot.png"
    plt.savefig(filename, format="png", dpi=300, bbox_inches="tight")
    print(f"Saved plot as {filename}")
    plt.close()

    #######################################################
    # Positiv and negative plot for inventors and applicants
    ########################################################
    import pandas as pd
    import matplotlib.pyplot as plt
    import numpy as np
    from pathlib import Path
    import re
    from typing import Optional

    # Classification function with PATSTAT psn_sector values
    def classify_entity(name: str, psn_sector: Optional[str] = None) -> str:
        """
        Classify a name as 'INDIVIDUAL' or 'NON_INDIVIDUAL' based on psn_sector or naming patterns.

        Args:
            name (str): The entity name (e.g., from person_name or psn_name).
            psn_sector (Optional[str]): Existing sector value, if available.

        Returns:
            str: 'INDIVIDUAL' or 'NON_INDIVIDUAL'.
        """
        # Define all expected PATSTAT psn_sector categories
        valid_sectors = {
            "INDIVIDUAL": "INDIVIDUAL",
            "COMPANY": "NON_INDIVIDUAL",
            "UNIVERSITY": "NON_INDIVIDUAL",
            "GOV NON-PROFIT": "NON_INDIVIDUAL",
            "GOVERNMENT": "NON_INDIVIDUAL",
            "HOSPITAL": "NON_INDIVIDUAL",
            "UNKNOWN": None,  # Trigger prediction for 'UNKNOWN'
            "": None,  # Trigger prediction for empty string
        }

        # If psn_sector is provided and in valid_sectors (not None), use it
        if (
            psn_sector
            and psn_sector.strip() in valid_sectors
            and valid_sectors[psn_sector.strip()] is not None
        ):
            return valid_sectors[psn_sector.strip()]

        # Predict based on name for missing, empty, 'UNKNOWN', or invalid psn_sector
        name = name.strip().upper()
        non_indiv_keywords = [
            "AS",
            "ASA",
            "INC",
            "LTD",
            "LLC",
            "CORP",
            "COMPANY",
            "TECHNOLOGIES",
            "TECH",
            "UNIVERSITY",
            "INSTITUTE",
            "GROUP",
            "INDUSTRY",
            "NORWAY",
            "SCANDINAVIA",
        ]
        if any(keyword in name for keyword in non_indiv_keywords):
            return "NON_INDIVIDUAL"

        parts = re.split(r"[,\s]+", name)
        if ("," in name or len(parts) >= 2) and not any(
            part in non_indiv_keywords for part in parts
        ):
            if any(len(part) <= 2 for part in parts) or len(parts) <= 4:
                return "INDIVIDUAL"

        return "NON_INDIVIDUAL"

    # Step 1: Clean and classify
    df_appl_invt["person_ctry_code"] = (
        df_appl_invt["person_ctry_code"].astype(str).str.strip()
    )
    df_appl_invt_cleaned = df_appl_invt[
        df_appl_invt["person_ctry_code"].notna()
        & (df_appl_invt["person_ctry_code"] != "")
        & (df_appl_invt["person_ctry_code"] != " ")
        & (df_appl_invt["person_ctry_code"].str.len() > 0)
    ].copy()

    # Apply classification using PATSTAT psn_sector values
    df_appl_invt_cleaned["psn_sector_predicted"] = df_appl_invt_cleaned.apply(
        lambda row: classify_entity(row["person_name"], row["psn_sector"]), axis=1
    )

    # Step 2: Categorize Inventors and Applicants
    # Inventors who are individuals
    inv_indiv_data = df_appl_invt_cleaned[
        (df_appl_invt_cleaned["invt_seq_nr"] > 0)
        & (df_appl_invt_cleaned["psn_sector_predicted"] == "INDIVIDUAL")
    ].copy()
    df_inv_indiv_counts = (
        inv_indiv_data.groupby(["docdb_family_id", "person_ctry_code"])
        .agg({"nb_inventors": "max"})
        .reset_index()
        .rename(columns={"nb_inventors": "inv_indiv_count"})
    )

    # Inventors who are not individuals
    inv_non_indiv_data = df_appl_invt_cleaned[
        (df_appl_invt_cleaned["invt_seq_nr"] > 0)
        & (df_appl_invt_cleaned["psn_sector_predicted"] == "NON_INDIVIDUAL")
    ].copy()
    df_inv_non_indiv_counts = (
        inv_non_indiv_data.groupby(["docdb_family_id", "person_ctry_code"])
        .agg({"nb_inventors": "max"})
        .reset_index()
        .rename(columns={"nb_inventors": "inv_non_indiv_count"})
    )

    # Applicants who are not individuals
    app_non_indiv_data = df_appl_invt_cleaned[
        (df_appl_invt_cleaned["applt_seq_nr"] > 0)
        & (df_appl_invt_cleaned["psn_sector_predicted"] == "NON_INDIVIDUAL")
    ].copy()
    df_app_non_indiv_counts = (
        app_non_indiv_data.groupby(["docdb_family_id", "person_ctry_code"])
        .agg({"nb_applicants": "max"})
        .reset_index()
        .rename(columns={"nb_applicants": "app_non_indiv_count"})
    )

    # Applicants who are individuals
    app_indiv_data = df_appl_invt_cleaned[
        (df_appl_invt_cleaned["applt_seq_nr"] > 0)
        & (df_appl_invt_cleaned["psn_sector_predicted"] == "INDIVIDUAL")
    ].copy()
    df_app_indiv_counts = (
        app_indiv_data.groupby(["docdb_family_id", "person_ctry_code"])
        .agg({"nb_applicants": "max"})
        .reset_index()
        .rename(columns={"nb_applicants": "app_indiv_count"})
    )

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

    # Sort by total 'NO' counts across all categories
    sort_country = "NO"
    total_no_counts = (
        inv_indiv_pivot.get(sort_country, pd.Series(0, index=inv_indiv_pivot.index))
        + inv_non_indiv_pivot.get(
            sort_country, pd.Series(0, index=inv_non_indiv_pivot.index)
        )
        + app_non_indiv_pivot.get(
            sort_country, pd.Series(0, index=app_non_indiv_pivot.index)
        )
        + app_indiv_pivot.get(sort_country, pd.Series(0, index=app_indiv_pivot.index))
    )
    sort_order = total_no_counts.sort_values(ascending=False).index
    inv_indiv_pivot = inv_indiv_pivot.loc[sort_order]
    inv_non_indiv_pivot = inv_non_indiv_pivot.loc[sort_order]
    app_non_indiv_pivot = app_non_indiv_pivot.loc[sort_order]
    app_indiv_pivot = app_indiv_pivot.loc[sort_order]

    # Plotting
    fig, ax = plt.subplots(figsize=(12, 8), dpi=300)
    bar_width = 0.4
    index = np.arange(len(inv_indiv_pivot))

    # Positive Left (Inventors - Individuals)
    bottom_inv_indiv = np.zeros(len(index))
    if sort_country in inv_indiv_pivot.columns:
        ax.bar(
            index,
            inv_indiv_pivot[sort_country],
            bar_width,
            bottom=bottom_inv_indiv,
            label=sort_country,
            color=color_map[sort_country],
        )
        bottom_inv_indiv += inv_indiv_pivot[sort_country]
    for country in inv_indiv_pivot.columns:
        if country != sort_country and inv_indiv_pivot[country].sum() > 0:
            ax.bar(
                index,
                inv_indiv_pivot[country],
                bar_width,
                bottom=bottom_inv_indiv,
                label=country,
                color=color_map[country],
            )
            bottom_inv_indiv += inv_indiv_pivot[country]

    # Negative Left (Inventors - Non-Individuals)
    bottom_inv_non_indiv = np.zeros(len(index))
    if sort_country in inv_non_indiv_pivot.columns:
        ax.bar(
            index,
            -inv_non_indiv_pivot[sort_country],
            bar_width,
            bottom=bottom_inv_non_indiv,
            label=sort_country if sort_country not in inv_indiv_pivot.columns else None,
            color=color_map[sort_country],
        )
        bottom_inv_non_indiv -= inv_non_indiv_pivot[sort_country]
    for country in inv_non_indiv_pivot.columns:
        if country != sort_country and inv_non_indiv_pivot[country].sum() > 0:
            already_labeled = (
                country in inv_indiv_pivot.columns
                and inv_indiv_pivot[country].sum() > 0
            )
            ax.bar(
                index,
                -inv_non_indiv_pivot[country],
                bar_width,
                bottom=bottom_inv_non_indiv,
                label=country if not already_labeled else None,
                color=color_map[country],
            )
            bottom_inv_non_indiv -= inv_non_indiv_pivot[country]

    # Positive Right (Applicants - Non-Individuals)
    bottom_app_non_indiv = np.zeros(len(index))
    if sort_country in app_non_indiv_pivot.columns:
        ax.bar(
            index + bar_width,
            app_non_indiv_pivot[sort_country],
            bar_width,
            bottom=bottom_app_non_indiv,
            label=sort_country if sort_country not in inv_indiv_pivot.columns else None,
            color=color_map[sort_country],
        )
        bottom_app_non_indiv += app_non_indiv_pivot[sort_country]
    for country in app_non_indiv_pivot.columns:
        if country != sort_country and app_non_indiv_pivot[country].sum() > 0:
            already_labeled = (
                country in inv_indiv_pivot.columns
                and inv_indiv_pivot[country].sum() > 0
            )
            ax.bar(
                index + bar_width,
                app_non_indiv_pivot[country],
                bar_width,
                bottom=bottom_app_non_indiv,
                label=country if not already_labeled else None,
                color=color_map[country],
            )
            bottom_app_non_indiv += app_non_indiv_pivot[country]

    # Negative Right (Applicants - Individuals)
    bottom_app_indiv = np.zeros(len(index))
    if sort_country in app_indiv_pivot.columns:
        ax.bar(
            index + bar_width,
            -app_indiv_pivot[sort_country],
            bar_width,
            bottom=bottom_app_indiv,
            label=sort_country if sort_country not in inv_indiv_pivot.columns else None,
            color=color_map[sort_country],
        )
        bottom_app_indiv -= app_indiv_pivot[sort_country]
    for country in app_indiv_pivot.columns:
        if country != sort_country and app_indiv_pivot[country].sum() > 0:
            already_labeled = (
                country in inv_indiv_pivot.columns
                and inv_indiv_pivot[country].sum() > 0
            )
            ax.bar(
                index + bar_width,
                -app_indiv_pivot[country],
                bar_width,
                bottom=bottom_app_indiv,
                label=country if not already_labeled else None,
                color=color_map[country],
            )
            bottom_app_indiv -= app_indiv_pivot[country]

    # Customize the plot
    ax.set_title(
        "Inventors and Applicants by Type and Country per docdb_family_id", fontsize=14
    )
    ax.set_xlabel("Inventors | Applicants", fontsize=12)
    ax.set_ylabel(
        "Count (Positive: Indiv Inv / Non-Indiv App, Negative: Non-Indiv Inv / Indiv App)",
        fontsize=12,
    )
    tick_positions = index + bar_width / 2
    tick_labels = [
        str(i + 1) for i in range(len(inv_indiv_pivot))
    ]  # Updated as per your previous request
    ax.set_xticks(tick_positions)
    ax.set_xticklabels(tick_labels, rotation=45, ha="right", fontsize=10)
    ax.legend(title="Country", bbox_to_anchor=(1.05, 1), loc="upper left", fontsize=10)
    ax.grid(axis="y", linestyle="--", alpha=0.7)

    # Set y-axis limits with 20% offset
    max_positive = max(bottom_inv_indiv.max(), bottom_app_non_indiv.max())
    max_negative = min(bottom_inv_non_indiv.min(), bottom_app_indiv.min())
    max_height = max(max_positive, abs(max_negative))
    y_offset = max_height * 0.2
    ax.set_ylim(max_negative - y_offset, max_height + y_offset)

    plt.tight_layout()

    # Save plot
    output_dir = Path("output_plots")
    output_dir.mkdir(exist_ok=True)
    filename = output_dir / "inventor_applicant_indiv_non_indiv_bar_plot.png"
    plt.savefig(filename, format="png", dpi=300, bbox_inches="tight")
    print(f"Saved plot as {filename}")
    plt.close()
