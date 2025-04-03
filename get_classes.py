#---------------------------------------
#   Get priority auth from docdb_family_id
# 

from shlex import join
import os,sys
import pandas as pd
from pandas import read_sql
#from sqlalchemy.util import py310 
from pathlib import Path
#import matplotlib.pyplot as plt
from connect_database import create_sqlalchemy_session
from sqlalchemy.orm import aliased
from sqlalchemy import distinct
from sqlalchemy import create_engine, text, Table, Column, Integer, String, MetaData, select, or_, and_
import logging
import csv
# Our functions
from extract_data import get_country
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



output_dir = Path(config.output_dir)  

 
# tables to work with
from models_tables import (
    TLS201_APPLN,
    TLS224_APPLN_CPC,
    TLS209_APPLN_IPC
)

# Create aliases for the models
t201 = aliased(TLS201_APPLN)
t224 = aliased(TLS224_APPLN_CPC)
t209 = aliased(TLS209_APPLN_IPC)

def get_classes_cpc(family_ids, batch_size=100):
    """
    Returns a list of tuples containing (docdb_family_id, class)
    for the specified docdb_family_ids, processed in batches.

    :param family_ids: List of docdb_family_ids to filter by
    :param batch_size: Number of IDs to process in each batch
    :return: List of tuples [(docdb_family_id, class), ...]
    """
    # Create a SQLAlchemy session
    db = create_sqlalchemy_session()
  
    from sqlalchemy import select, distinct

    results = []  # To store results from all batches

    # Process in batches
    for i in range(0, len(family_ids), batch_size):
        batch = family_ids[i:i + batch_size]

        # Define the main query for the current batch
        query = (
            select(
                distinct(t201.appln_id),
                t201.docdb_family_id,
                t224.cpc_class_symbol
            )
            .select_from(t201)
            .join(t224, t201.appln_id == t224.appln_id)
            .where(t201.docdb_family_id.in_(batch))  # Filter by the current batch
            .group_by(t201.appln_id, t201.docdb_family_id, t224.cpc_class_symbol)
            .order_by(t224.cpc_class_symbol.desc())
        )
        
        # Execute the query and fetch results
        result = db.execute(query).fetchall()
        results.extend(result)  # Append results from this batch

    return results  # Return all results as a list of tuples

def get_classes_ipc(family_ids, batch_size=100):
    """
    Returns a list of tuples containing (docdb_family_id, ipc_class_symbol)
    for the specified docdb_family_ids, processed in batches.

    :param family_ids: List of docdb_family_ids to filter by
    :param batch_size: Number of IDs to process in each batch
    :return: List of tuples [(docdb_family_id, ipc_class_symbol), ...]
    """
    # Create a SQLAlchemy session
    db = create_sqlalchemy_session()
  
    from sqlalchemy import select, distinct

    results = []  # To store results from all batches

    # Process in batches
    for i in range(0, len(family_ids), batch_size):
        batch = family_ids[i:i + batch_size]

        # Define the main query for the current batch
        query = (
            select(
                distinct(t209.appln_id),
                t201.docdb_family_id,
                t209.ipc_class_symbol
            )
            .select_from(t209)
            .join(t201, t209.appln_id == t201.appln_id)
            .where(t201.docdb_family_id.in_(batch))  # Filter by the current batch
            .group_by(t209.appln_id, t201.docdb_family_id, t209.ipc_class_symbol)
            .order_by(t209.ipc_class_symbol.desc())
        )
        
        # Execute the query and fetch results
        result = db.execute(query).fetchall()
        results.extend(result)  # Append results from this batch

    return results  # Return all results as a list of tuples    
    
def get_ipc_cpc_classes(family_ids):
    
    cpc_results = get_classes_cpc(family_ids)
    ipc_results = get_classes_ipc(family_ids)

    df_cpc = pd.DataFrame(cpc_results, columns=['appln_id', 'docdb_family_id', 'cpc_class_symbol'])
    df_ipc = pd.DataFrame(ipc_results, columns=['appln_id', 'docdb_family_id', 'ipc_class_symbol'])

    # Merge ipc and cpc, and get only main classes, and remove duplucated class.
    
    # Clean CPC classes from G06F 12/60 to G06F12
    logger.info("Cleaning CPC class data...")
    df_cpc['cpc_class_symbol'] = df_cpc['cpc_class_symbol'].str.split('/').str[0].str.replace(' ', '')
    df_cpc_grouped = df_cpc.groupby(['appln_id', 'docdb_family_id'])['cpc_class_symbol'].apply(
        lambda x: ', '.join(set(x))
    ).reset_index()

    # Clean IPC classes
    logger.info("Cleaning IPC class data...")
    df_ipc['ipc_class_symbol'] = df_ipc['ipc_class_symbol'].str.split('/').str[0].str.replace(' ', '')
    df_ipc_grouped = df_ipc.groupby(['appln_id', 'docdb_family_id'])['ipc_class_symbol'].apply(
        lambda x: ', '.join(set(x))
    ).reset_index()

    # Merge CPC and IPC classes
    logger.info("Merging CPC and IPC class data...")
    df_merged = pd.merge(df_cpc_grouped, df_ipc_grouped, on=['appln_id', 'docdb_family_id'], how='outer')

    # Save the merged DataFrame to a CSV file
    logger.info(f"Saving merged CPC/IPC class data to ... main_table_prio_class")
    df_merged.to_csv(output_dir / "main_table_prio_class.csv")

    return df_merged