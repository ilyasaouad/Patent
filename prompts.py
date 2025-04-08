PROMPTS = {
    "applicants_inventors_count": 
    """
    Please analyze this patent-related dataframe:

    DataFrame - {df_name}:
    {json_data1}

    Context:
    Please provide:

    1. Individual analysis for each dataframe:
       - Key metrics (unique patent families, country distribution)
       - Patterns in country representation
       - Notable outliers or unusual counts
       - Special focus on {country_code}'s role in the data

    2. Cross-dataframe analysis:
       - Identify patent families with interesting collaboration patterns
       - Compare applicant vs. inventor country distributions
       - Highlight cases of international collaboration
       - Analyze discrepancies between applicant countries and inventor countries

    3. Provide a concise summary that:
       - Identifies the central country/countries in this patent ecosystem
       - Characterizes the nature of international collaboration
       - Highlights the most notable patent families and why they're interesting
       - Describes the overall structure of innovation and ownership evident in the data

    Use specific examples from the data to support your observations and focus on patterns that reveal meaningful insights about patent collaboration networks.
    
    Provide text with clear and concise answers based on the data.
    """,
    "summary_applicants_inventors": 
    """
    Summarize these analyses:
    {combined_responses}
    """,
}