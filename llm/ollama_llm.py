# llm/ollama_llm.py
import requests
from typing import Optional, List
import logging
import json
from config import OLLAMA_BASE_URL, OLLAMA_MODEL, OLLAMA_TEMPERATURE
import aiohttp

logger = logging.getLogger(__name__)

class OllamaLLM:
    def __init__(self):
        self.base_url = "http://localhost:11434"
        self.model = "llama3:latest"
        self.temperature = OLLAMA_TEMPERATURE

    async def check_connection(self) -> bool:
        try:
            response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Ollama connection check failed: {e}")
            return False

    async def call(self, prompt: str) -> str:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False
                    }
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"Ollama API error: {error_text}")
                        
                    result = await response.json()
                    if "response" in result:
                        return result["response"]
                    else:
                        raise Exception("Invalid response format from Ollama")
                        
        except Exception as e:
            logger.error(f"Error communicating with Ollama: {e}")
            return f"Error: {str(e)}"