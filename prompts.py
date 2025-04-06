# prompts.py
PROMPTS = {
    "applicant_ratios": """
    Analyze the following DataFrame and provide insights:

    DataFrame:
    {json_data}

    Context:
    - The data is related to patent data
    - The DataFrame contains columns: 'country' of origin of the 'applicant', and 'docdb_family_id' as Id for a patent.
    - Each row represents a patent or patent family.

    Instructions:
    - Summarize the key trends in the data.
    - Identify the country that appears most frequently in the dataset and call it the "Country of Interest."
    - Identify the top 5 countries with the most applicants and their countries.
    - Identify the top 5 countries that collaborate most frequently with the "Country of Interest" (i.e., countries with common applicants in the same application/docdb_family_id).
    
    Please give me an analyse and NOT any script how to do it.
    
    Provide text with clear and concise answers based on the data.
    """,

    "inventor_ratios": """
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

    Please give me an analyse and NOT any script how to do it.
    
    Provide text with clear and concise answers based on the data.
    """,
    # Add more prompts here as needed
}