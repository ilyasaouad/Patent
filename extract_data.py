# Extract data related to origin country of applt and invt in date range years. 
# And store dataframe in database with table name 'patstat_COUNTRY_YEAR1_YEAR2 ALL or 50% ' 
import os,sys
from pathlib import Path
from connect_database import create_sqlalchemy_session
from sqlalchemy.orm import aliased
from sqlalchemy import  or_, and_
from sqlalchemy import func, case, or_
import pandas as pd
import config

 
    
# Create a SQLAlchemy session
db = create_sqlalchemy_session()

# Tables to work with
from models_tables import (
    TLS201_APPLN,
    TLS204_APPLN_PRIOR,
    TLS206_PERSON,
    TLS207_PERS_APPLN,
    TLS226_PERSON_ORIG
   )

# Create aliases for the models
t201 = aliased(TLS201_APPLN)
t204 = aliased(TLS204_APPLN_PRIOR)
t206 = aliased(TLS206_PERSON)
t207 = aliased(TLS207_PERS_APPLN)
t226 = aliased(TLS226_PERSON_ORIG)

# T is the threshold for the 50% condition of inventors, default is 0.5
 
def get_patent_country_code(T: float = 0.5):
    """
        Fetch patent data for a specific country and time period.
        Parameters:
            year_start (int): Start year for the dataset.
            year_end (int): End year for the dataset.
            country_code (str): ISO country code for the target country.
        Returns:
            tuple: Two DataFrames:
                - df_1appl_1invt: Data for 1 applicant and 1 inventor.
                - df_50_invt: Data where at least 50% of inventors are from the specified country.
        """
    # get constast from config.py
    country_code = config.country_code
    start_year = config.start_year
    end_year = config.end_year
    output_dir = Path(config.output_dir) 


    # Ensure the output directory exists
    # Check if the output directory exists
    if not os.path.exists(output_dir):
      # If it doesn't exist, create it
      os.makedirs(output_dir)
      print(f"Created output directory: {output_dir}")
    else:
      print(f"Output directory already exists: {output_dir}")
 

    # Create a SQLAlchemy session
    db = create_sqlalchemy_session()

    # Define aliases for the models
    t201 = aliased(TLS201_APPLN)
    t207 = aliased(TLS207_PERS_APPLN)
    t206 = aliased(TLS206_PERSON)

    # Step 1: Query for 1 Applicant and 1 Inventor
    query_1appl_1invt = (
        db.query(
            t201.appln_filing_year,
            t201.docdb_family_id,
            t201.appln_id,
            t201.appln_auth,
            t201.appln_nr,
            t206.psn_name,
            t206.person_name,
            t206.person_name_orig_lg,
            t206.psn_sector,
            t206.person_ctry_code,
            t207.applt_seq_nr,
            t207.invt_seq_nr,
        )
        .join(t207, t201.appln_id == t207.appln_id)
        .join(t206, t207.person_id == t206.person_id)
        .filter(
            t206.person_ctry_code == country_code,
            t201.appln_filing_year.between(start_year, end_year),
        )
        .order_by(t201.appln_filing_year, t201.appln_id, t201.appln_auth)
    )
    try:
        result_1appl_1invt = query_1appl_1invt.all()
    except Exception as e:
        print(f"Error fetching data for 1 applicant and 1 inventor: {e}")
        return None, None

    if not result_1appl_1invt:
        print("Warning: No data found for 1 applicant and 1 inventor.")
    else:
        print(f"Found {len(result_1appl_1invt)} rows for 1 applicant and 1 inventor.")

    df_1appl_1invt = pd.DataFrame(result_1appl_1invt)

    """
    Processes families with at least 50% inventors from the specified country.
    
    DataFrame containing families with at least 50% inventors from the country.
    """
    # Step 1: Count total inventors and inventors from the country per family
    inventor_counts = (
        df_1appl_1invt[df_1appl_1invt['invt_seq_nr'].notnull()]
        .groupby('docdb_family_id')
        .agg(
            total_inventors=('invt_seq_nr', 'count'),
            no_inventors=('person_ctry_code', lambda x: (x == country_code).sum())
        )
        .reset_index()
    )

    # Avoid division by zero
    inventor_counts['inventor_ratio'] = inventor_counts['no_inventors'] / inventor_counts['total_inventors']
    inventor_counts['inventor_ratio'] = inventor_counts['inventor_ratio'].fillna(0)

    # Step 2: Check if there's at least one applicant from the country per family
    applicant_check = (
        df_1appl_1invt[df_1appl_1invt['applt_seq_nr'].notnull()]
        .groupby('docdb_family_id')['person_ctry_code']
        .apply(lambda x: (x == country_code).any())
        .rename('has_no_applicant')
        .reset_index()
    )

    # Step 3: Merge inventor counts and applicant check
    family_data = pd.merge(inventor_counts, applicant_check, on='docdb_family_id', how='left')
    family_data['has_no_applicant'] = family_data['has_no_applicant'].fillna(False)

    # Step 4: Filter families based on criteria
    
    filtered_families = family_data[
        (family_data['has_no_applicant']) |
        ((family_data['total_inventors'] > 0) & (family_data['inventor_ratio'] >= T))
    ]

    if filtered_families.empty:
        print("Warning: No families meet the criteria of having 50% inventors from the country.")
        return pd.DataFrame()

    # Step 5: Join filtered families back to the original DataFrame
    result_df = pd.merge(
        df_1appl_1invt,
        filtered_families[['docdb_family_id']],
        on='docdb_family_id',
        how='inner'
    ).drop_duplicates()

    print(f"Found {len(result_df)} rows for families with 50% inventors.")
    
    df_50_invt = result_df

    # Save family_ids to file for future usage

    print(f"Output directory to save file----: {output_dir}")

    df_1appl_1invt['docdb_family_id'].to_csv(output_dir / '01_docdb_family_id_1appl_1invt.csv', index=False)
    df_50_invt['docdb_family_id'].to_csv(output_dir / '02_docdb_family_id_50_invt.csv', index=False)

    return df_1appl_1invt