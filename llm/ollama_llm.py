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

    def _validate_response(self, response_text: str) -> bool:
        """Validate if the response is meaningful."""
        # Check if response is empty or just whitespace
        if not response_text or not response_text.strip():
            return False
        
        # Check if response is too short or seems like an error message
        if len(response_text.strip()) < 10:
            return False
            
        return True

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
        
        # Format the prompt to be clear and specific
        formatted_prompt = f"""
Please provide a thorough code review for the following changes.
Focus on:
- Code quality
- Potential bugs
- Best practices
- Security issues

Changes to review:

{prompt}

Please provide specific, actionable feedback with examples where appropriate.
"""
        
        data = {
            "model": self.model,
            "prompt": formatted_prompt,
            "temperature": self.temperature,
            "stream": True
        }
        
        if stop:
            data["stop"] = stop

        try:
            logger.debug(f"Sending request to Ollama. URL: {self.base_url}/generate")
            logger.debug(f"Request data: {json.dumps(data, indent=2)}")
            
            response = requests.post(
                f"{self.base_url}/generate",  # Correct endpoint
                json=data,
                headers=headers,
                stream=True,
                timeout=30  # Add timeout
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
                        
                    except json.JSONDecodeError as e:
                        logger.warning(f"Failed to decode response chunk: {e}")
                        continue
            
            # Validate the response
            if not self._validate_response(full_response):
                logger.error("LLM returned invalid or empty response")
                return "Error: The language model returned an invalid response. Please try again."
            
            return full_response.strip()
            
        except requests.exceptions.Timeout:
            error_msg = "Request to Ollama timed out"
            logger.error(error_msg)
            return f"Error: {error_msg}"
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Error communicating with Ollama: {str(e)}"
            logger.error(error_msg)
            return f"Error: {error_msg}"
            
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(error_msg)
            return f"Error: {error_msg}"