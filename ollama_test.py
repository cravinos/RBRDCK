import requests
import json
import logging
from config import OLLAMA_MODEL, OLLAMA_BASE_URL

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_ollama():
    try:
        # List available models
        models_response = requests.get(f"{OLLAMA_BASE_URL}/api/tags")
        print("\nAvailable models:")
        print(json.dumps(models_response.json(), indent=2))
        
        # Test generation
        print(f"\nTesting generation with model: {OLLAMA_MODEL}")
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": "Write a simple Python function that adds two numbers."
            }
        )
        
        if response.status_code == 200:
            print("\nSuccessful test generation:")
            print(response.text)
        else:
            print(f"\nError: Status code {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_ollama()