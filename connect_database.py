import os
import urllib.parse
import pyodbc
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

# Get variables from environment
server = os.getenv('db_host')
database = os.getenv('db_database')
username = os.getenv('db_username')
password = os.getenv('db_password')

def connect_database():
    """Create a direct PyODBC connection"""
    try:
        conn_str = (
            'DRIVER={ODBC Driver 17 for SQL Server};'
            f'SERVER={server};'
            f'DATABASE={database};'
            f'UID={username};'
            f'PWD={password}'
        )
        conn = pyodbc.connect(conn_str)
        print("Database connection....OK...")
        return conn
    except pyodbc.Error as err:
        print(f"Error connecting to database: {err}")
        return None

def create_sqlalchemy_session():
    """Create SQLAlchemy session with proper connection string"""
    try:
        # First create the connection string
        conn_str = (
            'DRIVER={ODBC Driver 17 for SQL Server};'
            f'SERVER={server};'
            f'DATABASE={database};'
            f'UID={username};'
            f'PWD={password}'
        )
        
        # URL encode the connection string
        encoded_conn_str = urllib.parse.quote_plus(conn_str)
        
        # Create the full SQLAlchemy URL
        connection_url = f"mssql+pyodbc:///?odbc_connect={encoded_conn_str}"
        
        # Create the engine and session
        engine = create_engine(connection_url, echo=True)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        return session
        
    except Exception as e:
        print(f"Error creating SQLAlchemy session: {e}")
        return None