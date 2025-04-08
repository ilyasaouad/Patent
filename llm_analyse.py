import json
from chat_api_handel import OllamaChatAPIHandler
from prompts import PROMPTS   

def analyze_dataframe(dataframes_list: list, dataframe_names: list, prompt_name: str, country_code: str):    
    """
    Analyze a DataFrame using OllamaChatAPIHandler.

    Args:
        dataframes_list (list): List of DataFrames to analyze.
        dataframe_names (list): List of names corresponding to each DataFrame.
        prompt_name (str): The name of the prompt to use (must match a key in the PROMPTS dictionary).
        country_code (str, optional): Country code to focus on in the analysis. Defaults to "US".
    Returns:
        dict: A dictionary containing the DataFrame names and the response from Ollama.
    """
    if len(dataframes_list) != len(dataframe_names):
        raise ValueError("Number of DataFrames must match number of names.")
    
    if prompt_name not in PROMPTS:
        raise ValueError(f"Prompt '{prompt_name}' not found in PROMPTS.")
    
    individual_responses = []
    for df, name in zip(dataframes_list, dataframe_names):
        prompt_template = PROMPTS[prompt_name]
        prompt = prompt_template.format(
            df_name=name,
            json_data1=df.to_json(orient="split", index=False),
            country_code=country_code
        )
        response = OllamaChatAPIHandler.api_call(prompt)
        individual_responses.append({"df_name": name, "response": response})
    
    # Generate summary
    combined_responses = "\n\n".join([f"{r['df_name']}:\n{r['response']}" for r in individual_responses])
    summary_prompt = PROMPTS["summary_applicants_inventors"].format(combined_responses=combined_responses)
    summary_response = OllamaChatAPIHandler.api_call(summary_prompt)
    
    return {
        "individual_responses": individual_responses,
        "summary": summary_response
    }     