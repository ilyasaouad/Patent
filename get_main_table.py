#---------------------------------------
#  Get MAIN table data like t201_appln from Patstat IN BASIS OF DOCDB_FAMILY_ID 
#  stored in the output_dataframe. what was done in "extract_data.py" from main.py

import sys
import pandas as pd
from pathlib import Path
import csv
from sqlalchemy.orm import aliased
from sqlalchemy import create_engine, text, Table, Column, Integer, String, MetaData, select, or_, and_
from sqlalchemy.exc import SQLAlchemyError
import time
from datetime import datetime
# Our functions
from connect_database import create_sqlalchemy_session
import config
 
 
# Create a SQLAlchemy session
db = create_sqlalchemy_session()

# tables to work with
from models_tables import (
    TLS201_APPLN,
    TLS204_APPLN_PRIOR,
    TLS206_PERSON,
    TLS207_PERS_APPLN,
    TLS226_PERSON_ORIG
)

# Create aliases for the models
t201 = aliased(TLS201_APPLN)
t201_later = aliased(TLS201_APPLN)
t204 = aliased(TLS204_APPLN_PRIOR)
t206 = aliased(TLS206_PERSON)
t207 = aliased(TLS207_PERS_APPLN)
t226 = aliased(TLS226_PERSON_ORIG)

# Get and process data
#########
 
# df have large number of rows we process in batches
def main_table(family_ids, batch_size=500):
    """
    Process large patent dataset with progress tracking and memory management.
    
    Parameters:
    -----------
    family_ids : list or pandas.Series
        List of docdb_family_ids to query
    batch_size : int, optional
        Size of each batch (default: 500)
    
    Returns:
    --------
    pandas.DataFrame
        Combined DataFrame containing all query results
    """
    # Convert to list if input is pandas Series
    if isinstance(family_ids, pd.Series):
        family_ids = family_ids.tolist()
    
    # Initialize variables
    start_time = time.time()
    all_results = []
    total_ids = len(family_ids)
    processed_count = 0
    successful_queries = 0
    
    print(f"Starting process for {total_ids} family IDs at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Process in batches
    for i in range(0, total_ids, batch_size):
        batch_start_time = time.time()
        batch = family_ids[i:i + batch_size]
        
        try:
            # Build and execute query for current batch
            query = db.query(
                t201.appln_id,  
                t201.appln_auth,  
                t201.appln_nr,  
                t201.appln_kind,  
                t201.appln_filing_date,  
                t201.appln_filing_year,  
                t201.appln_nr_epodoc,  
                t201.appln_nr_original,  
                t201.ipr_type,  
                t201.receiving_office,  
                t201.internat_appln_id,  
                t201.int_phase,  
                t201.reg_phase,  
                t201.nat_phase,  
                t201.earliest_filing_date,  
                t201.earliest_filing_year,  
                t201.earliest_filing_id,  
                t201.earliest_publn_date,  
                t201.earliest_publn_year,  
                t201.earliest_pat_publn_id,  
                t201.granted,  
                t201.docdb_family_id,  
                t201.inpadoc_family_id,
                t201.docdb_family_size,  
                t201.nb_citing_docdb_fam,  
                t201.nb_applicants,  
                t201.nb_inventors  
                ).filter(
                    t201.docdb_family_id.in_(batch)
                ).order_by(
                    t201.appln_filing_year
                )
            
            batch_result = query.all()
            if batch_result:
                all_results.extend(batch_result)
                successful_queries += len(batch_result)
            
            processed_count += len(batch)
            
            # Calculate and display progress
            progress = (processed_count / total_ids) * 100
            batch_time = time.time() - batch_start_time
            elapsed_time = time.time() - start_time
            
            print(f"\rProgress: {progress:.1f}% ({processed_count}/{total_ids}) | "
                  f"Successful queries: {successful_queries} | "
                  f"Batch time: {batch_time:.2f}s | "
                  f"Total time: {elapsed_time:.2f}s", end="")
            
            # Optional: Clear memory every 10 batches
            if i % (batch_size * 10) == 0:
                db.expire_all()
                
        except SQLAlchemyError as e:
            print(f"\nDatabase error in batch {i//batch_size + 1}: {str(e)}")
            continue
        except Exception as e:
            print(f"\nUnexpected error in batch {i//batch_size + 1}: {str(e)}")
            continue
    
    # Create final DataFrame
    if all_results:
        final_df = pd.DataFrame(all_results)
        
        # Print final statistics
        end_time = time.time()
        total_time = end_time - start_time
        print(f"\n\nProcessing completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Total time: {total_time:.2f} seconds")
        print(f"Total records processed: {processed_count}")
        print(f"Successful queries: {successful_queries}")
        print(f"Final dataset size: {len(final_df)} rows")
        
        return final_df
    else:
        print("\nNo results found for any batch")
        return pd.DataFrame()

## Run the query
# Get family_ids / docdb_family_id from  docdb_family_id_1appl_1invt.csv in database.
# this file is created from "extract_data.py"

# Get output_dir from config.py and convert to Path object
output_dir = Path(config.output_dir)
print('--------------------------')
print(f"output_dir: {output_dir}")
print('--------------------------')
 
df_one_one = pd.read_csv(output_dir / 'docdb_family_id_1appl_1invt.csv') 

# get only the unique docdb_family_id, and reset index
df = df_one_one[['docdb_family_id']].drop_duplicates().reset_index(drop=True)

# make main table equivant to tls201_appln for our data
df_result = main_table(df['docdb_family_id'])

# Save results to a file
#file_ident = f"{1appl_1invt}"  
df_result.to_csv(output_dir / 'main_table_1appl_1invt.csv', index=False)

# the same for 50 inventors
df_50_invt = pd.read_csv(output_dir / 'docdb_family_id_50_invt.csv')
df = df_50_invt[['docdb_family_id']].drop_duplicates().reset_index(drop=True)

df_result = main_table(df['docdb_family_id'])

# Save results to a file
df_result.to_csv(output_dir / 'main_table_50_invt.csv', index=False)


#-----------------------------
# Store tables in database  
#-----------------------------
engine = db.get_bind()

table_name_1appl_1invt =  f"main_table_1appl_1invt"
table_name_50_invt =  f"main_table_50_invt"
 
# Store DataFrame to database
try:
    df_1appl_1invt.to_sql(
        table_name_1appl_1invt,     # table name
        engine,
        if_exists='replace',    # 'replace' will drop existing table, use 'append' to add data
        index=False,
        schema='dbo'           # default schema for MS SQL Server
    )
    print(f"Successfully added {table_name_1appl_1invt} to the database.")
except Exception as e:
    print(f"An error occurred while adding {table_name_1appl_1invt} to the database: {e}")
    
    # Store DataFrame to database
try:
    df_50_invt.to_sql(
        table_name_50_invt,     # table name
        engine,
        if_exists='replace',    # 'replace' will drop existing table, use 'append' to add data
        index=False,
        schema='dbo'           # default schema for MS SQL Server
    )
    print(f"Successfully added {table_name_50_invt} to the database.")
except Exception as e:
    print(f"An error occurred while adding {table_name_50_invt} to the database: {e}")
