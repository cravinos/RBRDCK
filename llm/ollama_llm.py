# llm/ollama_llm.py

import requests
from typing import Optional, List
import logging
import json
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
            logger.debug(f"Sending request to Ollama API. URL: {self.base_url}/api/generate")
            logger.debug(f"Request data: {json.dumps(data, indent=2)}")
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=data,
                headers=headers,
                stream=True
            )
            response.raise_for_status()
            
            text = ''
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8').strip()
                    logger.debug(f"Received line: {decoded_line}")
                    try:
                        json_line = json.loads(decoded_line)
                        text_chunk = json_line.get("response", "")
                        text += text_chunk
                    except json.JSONDecodeError as e:
                        logger.error(f"Error decoding JSON: {e}")
                        continue

            if not text.strip():
                logger.error("LLM returned an empty response")
                return "Error: The language model returned an empty response."
            
            logger.debug(f"Final response: {text}")
            return text.strip()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error communicating with the LLM: {e}", exc_info=True)
            return f"Error generating review: {str(e)}"