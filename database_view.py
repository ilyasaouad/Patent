import sys
from connect_database import create_sqlalchemy_session
import pandas as pd
from tabulate import tabulate
 
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
session = create_sqlalchemy_session()
print(session)

query = text("SELECT * FROM TLS201_APPLN WHERE docdb_family_id = 89029748")
# query = text("SELECT name FROM sys.databases")

# Execute the query with the parameter for the username
result = session.execute(query, {"username": "patstatuser"})

# Fetch all results
rows = result.fetchall()

pd.set_option('display.max_columns', None)
df = pd.DataFrame(rows)

print(df)

sys.exit()

# Print the result
for row in rows:
    print(f'username: {row[0]}, database_name: {row[1]}')

sys.exit()

query = text("SELECT name, default_database_name FROM sys.sql_logins WHERE name = :username")
# query = text("SELECT name FROM sys.databases")

# Execute the query with the parameter for the username
result = session.execute(query, {"username": "patstatuser"})

# Fetch all results
rows = result.fetchall()

# Print the result
for row in rows:
    print(f'username: {row[0]}, database_name: {row[1]}')

# Define the query to get the full server name (MachineName and InstanceName)
query = text("""
SELECT 
    SERVERPROPERTY('MachineName') AS MachineName,
    SERVERPROPERTY('InstanceName') AS InstanceName
""")

# Execute the query
result = session.execute(query)

# Fetch the result
server_info = result.fetchone()

# Get the full server name or instance name
machine_name = server_info[0]  # MachineName is the first column
instance_name = server_info[1]  # InstanceName is the second column

if instance_name:
    server_path = f"{machine_name}\\{instance_name}"
else:
    server_path = machine_name  # Default instance, just machine name

print(f"Server connection string: {server_path}")

sys.exit()

# Execute raw SQL query
sql_query = text("SELECT * FROM INFORMATION_SCHEMA.TABLES")
result = session.execute(sql_query)

# Print results
for row in result:
    print('Tables:',row)

# select tables
sql_query = text("SELECT top 2 * FROM  tls201_appln" )    
result = session.execute(sql_query)
 
df = pd.DataFrame(result)

# Use tabulate for a prettier display
pd.set_option('display.max_columns', None)  # Show all columns (if needed)
print(tabulate(df, headers='keys', tablefmt='psql'))


 




