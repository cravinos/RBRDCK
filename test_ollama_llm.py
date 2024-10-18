# test_ollama_llm.py

from llm.ollama_llm import OllamaLLM

def test_ollama_llm():
    llm = OllamaLLM()
    prompt = "What is the capital of France?"
    response = llm.call(prompt)
    print("LLM Response:", response)
    print("Type of response:", type(response))

if __name__ == "__main__":
    test_ollama_llm()
