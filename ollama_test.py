# ollama_test.py

from llm.ollama_llm import OllamaLLM
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_ollama():
    llm = OllamaLLM()
    
    test_prompts = [
        "Hello, how are you?",
        "What is 2 + 2?",
        "Explain what a for loop is in Python."
    ]
    
    for prompt in test_prompts:
        logger.info(f"Testing prompt: {prompt}")
        response = llm.call(prompt)
        logger.info(f"Response: {response}")
        print("\n")

if __name__ == "__main__":
    test_ollama()