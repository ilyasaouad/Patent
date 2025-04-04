import csv
import json
import pandas as pd 
from pathlib import Path
from pandas import read_csv
from  config import Config
from chat_api_handel import OllamaChatAPIHandler


output_dir = Path(Config.output_dir) 
 
path_to_file = output_dir/'data/applicants_inventors'
file = 'inventor_counts.csv'

# Open the CSV file
with open(path_to_file/file, mode='r', newline='') as csv_file:
    # Read the CSV file
    csv_reader = csv.DictReader(csv_file)
    
    # Convert CSV rows to a list of dictionaries
    data = list(csv_reader)

# Convert the list of dictionaries to JSON
json_data = json.dumps(data, indent=4)

# Join the list into a single string with newlines or spaces
PROMPT_TEMPLATE = f"""
Analyze the following DataFrame and provide insights:

DataFrame:
{json_data}

Context:
- The DataFrame contains columns: 'country', 'inventor', 'applicant', and 'docdb_family_id'.
- Each row represents a patent or patent family.

Instructions:
- Summarize the key trends in the data.
- Identify the country that appears most frequently in the dataset and call it the "Country of Interest."
- Identify the top 5 countries with the most inventors and applicants.
- Identify the top 5 countries that collaborate most frequently with the "Country of Interest" (i.e., countries with common inventors in the same application/docdb_family_id).

Provide clear and concise answers based on the data.
"""
# Print the resulting prompt
print(PROMPT_TEMPLATE)

# Call the API
response = OllamaChatAPIHandler.api_call(PROMPT_TEMPLATE)

# Print the response
print(response)
