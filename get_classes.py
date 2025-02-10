#---------------------------------------
#   Get priority auth from docdb_family_id
# 

from shlex import join
import os,sys
import numpy as np
import pandas as pd
from pandas import read_sql
from sqlalchemy.util import py310
import xlsxwriter 
import openpyxl
import os
from os import path
import matplotlib.pyplot as plt
from connect_database import create_sqlalchemy_session
from sqlalchemy.orm import aliased, sessionmaker
from sqlalchemy import distinct
import pandas as pd
from sqlalchemy import create_engine, text, Table, Column, Integer, String, MetaData, select, or_, and_
import csv
from extract_data import get_patent_country_code


working_dir = "C:/Users/iao/Desktop/PatStat_videre2/Patent_Familier_2024/patent_analyse/"

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
    
 