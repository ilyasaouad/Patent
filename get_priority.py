    #---------------------------------------
#   Get priority auth from docdb_family_id
# 
from pathlib import Path
from shlex import join
import pandas as pd
from pandas import read_sql
from pathlib import Path
from connect_database import create_sqlalchemy_session
from sqlalchemy.orm import aliased
from sqlalchemy import distinct
from sqlalchemy import create_engine, text, Table, Column, Integer, String, MetaData, select, or_, and_
import csv
# Our functions
from extract_data import get_patent_country_code
import config

working_dir = "C:/Users/iao/Desktop/PatStat_videre2/Patent_Familier_2024/patent_analyse/"

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
t204 = aliased(TLS204_APPLN_PRIOR)
t206 = aliased(TLS206_PERSON)
t207 = aliased(TLS207_PERS_APPLN)
t226 = aliased(TLS226_PERSON_ORIG)

def get_priority_auth(family_ids,batch_size=100):
    """
    Returns a list of tuples containing (docdb_family_id, priority_auth)
    for the specified docdb_family_ids, processed in batches.

    :param family_ids: List of docdb_family_ids to filter by
    :param batch_size: Number of IDs to process in each batch
    :return: List of tuples [(docdb_family_id, priority_auth), ...]
    """
    # Get output_dir from config.py and convert to Path object
    output_dir = Path(config.output_dir)

    # Create a SQLAlchemy session
    db = create_sqlalchemy_session()
  
    # Define aliases for tables to avoid ambiguity
    priority = aliased(t201, name="priority")
    later = aliased(t201, name="later")

    results = []  # To store results from all batches

    # Process in batches
    for i in range(0, len(family_ids), batch_size):
        batch = family_ids[i:i + batch_size]

        # Subquery: Select priority_auth, family_id, and later_docdb_family_id
        subquery = (
            select(
                priority.appln_auth.label("priority_auth"),
                priority.docdb_family_id.label("family_id"),
                later.docdb_family_id.label("later_docdb_family_id")
            )
            .select_from(priority)
            .join(t204, priority.appln_id == t204.prior_appln_id)
            .join(later, t204.appln_id == later.appln_id)
            .where(priority.docdb_family_id.in_(batch))  # Dynamic filtering for the batch
            .subquery()
        )

        # Main query: Join subquery with tls201_appln and select distinct values
        main_query = (
            select(
                distinct(subquery.c.family_id).label("docdb_family_id"),
                subquery.c.priority_auth
            )
            .select_from(t201)
            .join(subquery, subquery.c.family_id == t201.docdb_family_id)
        )

        # Execute the query and fetch results
        result = db.execute(main_query).fetchall()
        results.extend(result)  # Append results from this batch


        # Convert results to a DataFrame and save
        ids_priority_auth = pd.DataFrame(results, columns=["docdb_family_id", "priority_auth"])
        ids_priority_auth.to_csv(output_dir / '04_priority_auth_1appl_1invt.csv', index=False)

    return ids_priority_auth



 