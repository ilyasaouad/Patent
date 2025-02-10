# Extract data related to origin country of applt and invt in date range years. 
# And store dataframe in database with table name 'patstat_COUNTRY_YEAR1_YEAR2 ALL or 50% ' 
import os,sys
from connect_database import create_sqlalchemy_session
from sqlalchemy.orm import aliased
from sqlalchemy import  or_, and_
from sqlalchemy import func, case, or_
import pandas as pd

def get_patent_country_code(year_start, year_end, country_code, output_dir):
    
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


    # Define the first query to get applications based on the inventor's country
    q = db.query(
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
    ).join(
        t207, t201.appln_id == t207.appln_id
    ).join(
        t206, t207.person_id == t206.person_id
    ).filter(
        t206.person_ctry_code == country_code,
        t201.appln_filing_year.between(year_start, year_end) 
    ).order_by(
        t201.appln_filing_year, t201.appln_id, t201.appln_auth
    )  # Limit to 10 records for testing

    try:
        result = q.all()  # fetch the query result
    except Exception as e:
        print(f"An error occurred for fetching data: {e}")

    df_1appl_1invt = pd.DataFrame(result)

    # Define the second query to filter patent families based on criteria
    inventor_subquery = db.query(
        t201.docdb_family_id,
        func.count(t207.person_id).label('total_inventors'),
        func.sum(case((t206.person_ctry_code == country_code, 1), else_=0)).label('no_inventors')
    ).join(
        t207, t201.appln_id == t207.appln_id
    ).join(
        t206, t207.person_id == t206.person_id
    ).filter(
        t207.invt_seq_nr.isnot(None)
    ).group_by(
        t201.docdb_family_id
    ).subquery()

    applicant_subquery = db.query(
        t201.docdb_family_id,
        func.max(case((t206.person_ctry_code == country_code, 1), else_=0)).label('has_no_applicant')
    ).join(
        t207, t201.appln_id == t207.appln_id
    ).join(
        t206, t207.person_id == t206.person_id
    ).filter(
        t207.applt_seq_nr.isnot(None)
    ).group_by(
        t201.docdb_family_id
    ).subquery()

    # Main query to filter patent families based on the criteria
    q = db.query(
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
        inventor_subquery.c.total_inventors,
        inventor_subquery.c.no_inventors,
        applicant_subquery.c.has_no_applicant
    ).join(
        inventor_subquery, t201.docdb_family_id == inventor_subquery.c.docdb_family_id
    ).join(
        applicant_subquery, t201.docdb_family_id == applicant_subquery.c.docdb_family_id
    ).filter(
        or_(
            applicant_subquery.c.has_no_applicant == 1,
            (inventor_subquery.c.no_inventors / inventor_subquery.c.total_inventors) >= 0.5
        )
    ).filter(
        t201.appln_filing_year.between(year_start, year_end)
    ).distinct()

    try:
        result = q.all()  # fetch the query result
    except Exception as e:
        print(f"An error occurred for fetching data: {e}")

    df_50_invt = pd.DataFrame(result)

    # Extract and save docdb_family_id to csv file for future usage
    df_docdb_family_id_1appl_1invt = df_1appl_1invt['docdb_family_id'].drop_duplicates()
    df_docdb_family_id_1appl_1invt.to_csv(output_dir / 'docdb_family_id_1appl_1invt.csv', index=False)

    df_docdb_family_id_50_invt = df_50_invt['docdb_family_id'].drop_duplicates()
    df_docdb_family_id_50_invt.to_csv(output_dir / 'docdb_family_id_50_invt.csv', index=False)

    # Save to csv files
    file_name_1appl_1invt =  f"country_{country_code}_{year_start}_{year_end}_1appl_1invt"
    file_name_50_invt =  f"country_{country_code}_{year_start}_{year_end}_50_invt" 

    # Use the / operator to combine Path objects with file names
    df_1appl_1invt.to_csv(output_dir / (file_name_1appl_1invt + '.csv'), index=False)
    df_50_invt.to_csv(output_dir / (file_name_50_invt + '.csv'), index=False)
    
     
    #-----------------------------
    # Store tables in database  
    #-----------------------------
    engine = db.get_bind()

    table_name_1appl_1invt =  f"country_{country_code}_{year_start}_{year_end}_1appl_1invt"
    table_name_50_invt =  f"country_{country_code}_{year_start}_{year_end}_50_invt"
 
    # Store DataFrame to database
    try:
        df_1appl_1invt.to_sql(
            table_name_1appl_1invt,     # table name
            engine,
            if_exists='replace',    # 'replace' will drop existing table, use 'append' to add data
            index=False,
            schema='dbo'           # default schema for MS SQL Server
        )
        print(f"Successfully added {table_name_all} to the database.")
    except Exception as e:
        print(f"An error occurred while adding {table_name_all} to the database: {e}")
        
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
 