import json
from chat_api_handel import OllamaChatAPIHandler
from prompts import PROMPTS   

def analyze_dataframe(df, prompt_name: str, df_name: str):
    """
    Analyze a DataFrame using OllamaChatAPIHandler.

    Args:
        df (pd.DataFrame): The DataFrame to analyze.
        prompt_name (str): The name of the prompt to use (must match a key in the PROMPTS dictionary).
        df_name (str): A unique identifier for the DataFrame (e.g., its name).

    Returns:
        dict: A dictionary containing the DataFrame name and the response from Ollama.
    """
    # Serialize the DataFrame to JSON
    json_data = df.to_json(orient="split", index=False)

    # Get the prompt template
    if prompt_name not in PROMPTS:
        raise ValueError(f"Prompt '{prompt_name}' not found in the PROMPTS dictionary.")
    
    prompt_template = PROMPTS[prompt_name]

    # Construct the prompt
    prompt = prompt_template.format(json_data=json_data)

    # Call the API
    response = OllamaChatAPIHandler.api_call(prompt)

    # Return the result as a dictionary
    return {
        "df_name": df_name,
        "response": response
    }