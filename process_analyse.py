from operator import contains
import os
import sys
import pandas as pd
import numpy as np
from pathlib import Path
#from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, text
import logging
# Our functions
from connect_database import create_sqlalchemy_session
import config


# Initialize Logger 
logger = logging.getLogger(__name__)
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)   

# if i want to work with the database
# Create a SQLAlchemy session
db = create_sqlalchemy_session()

# Read from files from outdir_dir
outdir_dir = Path(config.output_dir) 

########### Function that calculate inventors fractional_counts per country
## number of inventors for a country per patent, exp NO 60%, US 40%..
import pandas as pd

def compute_fractional_counts(df):
    """
    Computes the fractional count of inventors per country (person_ctry_code) from the given DataFrame.

    Parameters:
        df (pd.DataFrame): Input DataFrame containing patent and inventor information.

    Returns:
        pd.DataFrame: A DataFrame with columns ['person_ctry_code', 'fractional_count'], sorted by fractional_count in descending order.
    """
    if df.empty:
        raise ValueError("Input DataFrame is empty.")

    # Step 1: Compute t1 (country-level count of inventors per patent)
    t1 = (
        df[df['invt_seq_nr'] > 0]  # Filter rows with invt_seq_nr > 0
        .groupby(['appln_id', 'person_ctry_code'], as_index=False)  # Group by appln_id and person_ctry_code
        .agg({'invt_seq_nr': 'count'})  # Count the number of inventors per country per patent
        .rename(columns={'invt_seq_nr': 'tot_in_ctry'})  # Rename the count column
    )

    # Step 2: Compute t2 (total count of inventors per patent)
    t2 = (
        df.groupby('appln_id', as_index=False)  # Group by appln_id
        .agg({'invt_seq_nr': 'max'})  # Get the maximum invt_seq_nr for each patent
        .rename(columns={'invt_seq_nr': 'tot_in_patent'})  # Rename the max column
        .query('tot_in_patent > 0')  # Filter patents with at least one inventor
    )

    # Step 3: Merge t1 and t2 with the original DataFrame
    merged_df = (
        df[['appln_id']].drop_duplicates()  # Start with unique appln_ids
        .merge(t1, on='appln_id', how='left')  # Left join with t1
        .merge(t2, on='appln_id', how='left')  # Left join with t2
        .fillna({'person_ctry_code': '', 'tot_in_ctry': 1, 'tot_in_patent': 1})  # Handle null values
    )

    # Step 4: Calculate fractional counts
    fractional_counts = (
        merged_df
        .assign(fractional_count=lambda x: x['tot_in_ctry'] / x['tot_in_patent'])  # Compute fractional count
        .groupby('person_ctry_code', as_index=False)  # Group by person_ctry_code
        .agg({'fractional_count': 'sum'})  # Sum the fractional counts
        .sort_values(by='fractional_count', ascending=False)  # Sort by fractional count in descending order
    )

    return fractional_counts


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

df = pd.read_csv(outdir_dir / "06_main_table_prio_names_classes.csv")

# This should be done in main.
df = clean_merged_dataframe(df)

country_code = config.country_code
T = 0.2

df_1appl_1invt = df
############ Testing number % of inventors from country ############
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

print(inventor_counts)

 

# Avoid division by zero
inventor_counts['inventor_ratio'] = inventor_counts['no_inventors'] / inventor_counts['total_inventors']
inventor_counts['inventor_ratio'] = inventor_counts['inventor_ratio'].fillna(0)

print(inventor_counts)



# Step 2: Check if there's at least one applicant from the country per family
applicant_check = (
    df_1appl_1invt[df_1appl_1invt['applt_seq_nr'].notnull()]
    .groupby('docdb_family_id')['person_ctry_code']
    .apply(lambda x: (x == country_code).any())
    .rename('has_no_applicant')
    .reset_index()
)

print(applicant_check)


# Step 3: Merge inventor counts and applicant check
family_data = pd.merge(inventor_counts, applicant_check, on='docdb_family_id', how='left')
family_data['has_no_applicant'] = family_data['has_no_applicant'].fillna(False)



# Step 4: Filter families based on criteria
filtered_families = family_data[(family_data['has_no_applicant']) | ((family_data['total_inventors'] > 0) & (family_data['inventor_ratio'] >= 0.9))]

# Step 5: Join filtered families back to the original DataFrame
result_df = pd.merge(
    df_1appl_1invt,
    filtered_families[['docdb_family_id']],
    on='docdb_family_id',
    how='inner'
).drop_duplicates()

print(f"Found {len(result_df)} rows for families with 50% inventors.")

sys.exit()

df_50_invt = result_df

print(df_50_invt.shape)


#############################################
sys.exit()

# Make new column Simple Family countries that will contains  countries familie nembers
# Step 1: Create a mapping of appln_id to all unique appln_auth values
auth_mapping = df.groupby("docdb_family_id")["appln_auth"].unique().to_dict()

# Debugging: Print the auth_mapping to verify its structure
print("Auth Mapping:")
for key, value in auth_mapping.items():
    print(f"{key}: {value.tolist()}")  # Convert NumPy arrays to lists for readability

# Step 2: Define the function to compute sf_countries for each row
def get_sf_countries(row):
    all_auths = auth_mapping.get(row["docdb_family_id"], np.array([]))  # Get all appln_auth for the appln_id
    all_auths_list = all_auths.tolist() if isinstance(all_auths, np.ndarray) else list(all_auths)  # Convert to list
    current_auth = row["appln_auth"]  # Get the current row's appln_auth
    
    # Exclude the current_auth and join the remaining values
    sf_countries = ",".join([auth for auth in all_auths_list if auth != current_auth])
    return sf_countries

# Apply the function to create the new column 'sf_countries'
df["sf_countries"] = df.apply(get_sf_countries, axis=1)

  
# Create the 'application' column
df['application'] = df['appln_auth'] + df['appln_nr'].str.strip() + df['appln_kind'].str.strip()
df.insert(0, 'application', df.pop('application'))
 
# Create Simple Family Nembers
# Create a mapping of docdb_family_id to all unique application values
auth_mapping = df.groupby("docdb_family_id")["application"].unique().to_dict()

# Debugging: Print the auth_mapping to verify its structure
print("Auth Mapping:")
for key, value in auth_mapping.items():
    print(f"{key}: {value.tolist()}")  # Convert NumPy arrays to lists for readability

# Step 2: Define the function to compute sf_countries for each row
def get_simple_family_members(row):
    all_auths = auth_mapping.get(row["docdb_family_id"], np.array([]))  # Get all appln_auth for the appln_id
    all_auths_list = all_auths.tolist() if isinstance(all_auths, np.ndarray) else list(all_auths)  # Convert to list
    current_auth = row["application"]  # Get the current row's appln_auth
    
    # Exclude the current_auth and join the remaining values
    sf_countries = ",".join([auth for auth in all_auths_list if auth != current_auth])
    return sf_countries

# Apply the function to create the new column 'sf_countries'
df["simple_family_members"] = df.apply(get_simple_family_members, axis=1)

 
# TESTING with docdb_family_id ==  57045679
df_2 = df[df['docdb_family_id'] ==  57045679]
#df_2 = df_2[['application','earliest_publn_date']]
#df_2.sort_values(by='earliest_publn_date', ascending=True, inplace=True)

#pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
#print(df_2[['sf_countries','simple_family_members']])

# Keep only the earliest filing date and filter out all other application in family
df_earliest = df.loc[df.groupby('docdb_family_id')['earliest_filing_date'].idxmin()]
pd.set_option('display.max_rows', None)
print(df[['person_ctry_code']].nunique())

sys.exit()

fractional_counts_df = compute_fractional_counts(df_earliest)

print(fractional_counts_df)