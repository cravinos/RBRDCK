# llm/ollama_llm.py
import requests
from typing import Optional, List
import logging
import json
from config import OLLAMA_BASE_URL, OLLAMA_MODEL, OLLAMA_TEMPERATURE

logger = logging.getLogger(__name__)

class OllamaLLM:
    def __init__(self):
        self.base_url = OLLAMA_BASE_URL.rstrip('/')  # Remove trailing slash if present
        self.model = OLLAMA_MODEL
        self.temperature = OLLAMA_TEMPERATURE

    def call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        """
        Call the Ollama API with proper error handling and validation.
        
        Args:
            prompt (str): The prompt to send to the LLM
            stop (Optional[List[str]]): Optional stop sequences
            
        Returns:
            str: The LLM's response or an error message
        """
        headers = {
            "Content-Type": "application/json",
        }
        
        data = {
            "model": self.model,
            "prompt": prompt,
            "stream": True
        }
        
        if self.temperature is not None:
            data["temperature"] = self.temperature
            
        if stop:
            data["stop"] = stop

        try:
            logger.debug(f"Sending request to Ollama. URL: {self.base_url}/api/generate")
            logger.debug(f"Using model: {self.model}")
            logger.debug(f"Request data: {json.dumps(data, indent=2)}")
            
            response = requests.post(
                f"{self.base_url}/api/generate",  # Use the correct endpoint
                json=data,
                headers=headers,
                stream=True,
                timeout=30
            )
            
            # Check for HTTP errors
            response.raise_for_status()
            
            full_response = ''
            for line in response.iter_lines():
                if line:
                    try:
                        json_response = json.loads(line.decode('utf-8'))
                        response_chunk = json_response.get("response", "")
                        full_response += response_chunk
                        logger.debug(f"Received chunk: {response_chunk}")
                        
                    except json.JSONDecodeError as e:
                        logger.warning(f"Failed to decode response chunk: {e}")
                        continue
            
            if not full_response.strip():
                logger.error("LLM returned empty response")
                return "Error: The language model returned an empty response."
            
            return full_response.strip()
            
        except requests.exceptions.Timeout:
            error_msg = "Request to Ollama timed out after 30 seconds"
            logger.error(error_msg)
            return f"Error: {error_msg}"
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Error communicating with Ollama: {str(e)}"
            logger.error(error_msg)
            if "404" in str(e):
                error_msg += "\nPlease ensure Ollama is running and the model is installed."
            return f"Error: {error_msg}"
            
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(error_msg)
            return f"Error: {error_msg}"