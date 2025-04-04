import requests
from config import Config

class OllamaChatAPIHandler:

    @classmethod
    def api_call(cls, prompt: str):
        """
        Send a prompt to Ollama and return the response.

        Args:
            prompt (str): The prompt to send to the model.

        Returns:
            str: The response from the model.
        """
        data = {
            "model": Config.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False
        }
        try:
            response = requests.post(url=Config.ollama_base_url + "/api/chat", json=data)
            response.raise_for_status()  # Raise an exception for HTTP errors
            json_response = response.json()
            if "error" in json_response:
                return f"OLLAMA ERROR: {json_response['error']}"
            return json_response["message"]["content"]
        except requests.exceptions.RequestException as e:
            return f"NETWORK ERROR: {str(e)}"