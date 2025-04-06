import sys
import os
import requests
from config import Config
import logging
from dotenv import load_dotenv

load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')

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
        # Prepare the payload
        data = {
            "model": Config.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False
        }

        try:
            # Make the POST request with a timeout
            response = requests.post(
                url=Config.ollama_base_url + "/api/chat",
                json=data,
                #timeout=10  # Timeout after 10 seconds
            )
            response.raise_for_status()  # Raise an exception for HTTP errors
            
            # Parse the JSON response
            json_response = response.json()

            # Check for errors in the response
            if "error" in json_response:
                logging.error(f"OLLAMA ERROR: {json_response['error']}")
                return f"OLLAMA ERROR: {json_response['error']}"

            # Ensure the expected structure is present
            if "message" in json_response and "content" in json_response["message"]:
                return json_response["message"]["content"]
            else:
                logging.error("Unexpected response structure from Ollama API")
                return "ERROR: Unexpected response structure from Ollama API"

        except requests.exceptions.HTTPError as http_err:
            logging.error(f"HTTP error occurred: {http_err}")
            return f"HTTP ERROR: {str(http_err)}"
        except requests.exceptions.RequestException as req_err:
            logging.error(f"Network error occurred: {req_err}")
            return f"NETWORK ERROR: {str(req_err)}"
        except ValueError as json_err:
            logging.error(f"JSON decoding error: {json_err}")
            return "ERROR: Invalid JSON response from server"

class OpenAIChatAPIHandler:

    @classmethod
    def api_call(cls, prompt: str):
        """
        Send a prompt to OpenAI and return the response.

        Args:
            prompt (str): The prompt to send to the model.

        Returns:
            str: The response from the model.
        """
        # Prepare the payload
        data = {
            "model": Config.openai_model_name,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {Config.openai_api_key}"
        }

        try:
            # Make the POST request with a timeout
            response = requests.post(
                url="https://api.openai.com/v1/chat/completions",
                json=data,
                headers=headers,
                #timeout=10  # Timeout after 10 seconds
            )
            response.raise_for_status()  # Raise an exception for HTTP errors
            
            # Parse the JSON response
            json_response = response.json()

            # Check for errors in the response
            if "error" in json_response:
                logging.error(f"OPENAI ERROR: {json_response['error']['message']}")
                return f"OPENAI ERROR: {json_response['error']['message']}"

            # Ensure the expected structure is present
            if "choices" in json_response and len(json_response["choices"]) > 0:
                return json_response["choices"][0]["message"]["content"]
            else:
                logging.error("Unexpected response structure from OpenAI API")
                return "ERROR: Unexpected response structure from OpenAI API"

        except requests.exceptions.HTTPError as http_err:
            logging.error(f"HTTP error occurred: {http_err}")
            return f"HTTP ERROR: {str(http_err)}"
        except requests.exceptions.RequestException as req_err:
            logging.error(f"Network error occurred: {req_err}")
            return f"NETWORK ERROR: {str(req_err)}"
        except ValueError as json_err:
            logging.error(f"JSON decoding error: {json_err}")
            return "ERROR: Invalid JSON response from server"