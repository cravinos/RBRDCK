# llm/ollama_llm.py

import requests
from typing import Optional, List
import logging
import json  # Import the json module to parse JSON responses
from config import OLLAMA_BASE_URL, OLLAMA_MODEL, OLLAMA_TEMPERATURE

logger = logging.getLogger(__name__)

class OllamaLLM:
    def __init__(self):
        self.base_url = OLLAMA_BASE_URL
        self.model = OLLAMA_MODEL
        self.temperature = OLLAMA_TEMPERATURE

    def call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        headers = {
            "Content-Type": "application/json",
        }
        data = {
            "model": self.model,
            "prompt": prompt,
            "temperature": self.temperature,
        }
        if stop:
            data["stop"] = stop

        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=data,
                headers=headers,
                stream=True  # Enable streaming response
            )
            response.raise_for_status()
            # Collect the 'response' field from each JSON chunk
            text = ''
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8').strip()
                    try:
                        json_line = json.loads(decoded_line)
                        text_chunk = json_line.get("response", "")
                        text += text_chunk
                    except json.JSONDecodeError as e:
                        logger.error(f"Error decoding JSON: {e}")
                        continue
            return text.strip()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error communicating with the LLM: {e}")
            return "Error generating review."
