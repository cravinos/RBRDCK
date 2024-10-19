# config.py

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# GitHub Configuration
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
if not GITHUB_TOKEN:
    raise ValueError("Please set your GitHub token in the .env file.")
REPO_USER = os.getenv("REPO_USER")
REPO_NAME = os.getenv("REPO_NAME")
if not REPO_USER:
    raise ValueError("REPO_USER not set in environment variables")
if not REPO_NAME:
    raise ValueError("REPO_NAME not set in environment variables")

# LLM Configuration
OLLAMA_BASE_URL = "http://localhost:11434"  # Update if necessary
OLLAMA_MODEL = "llama3:latest"  # Replace with your installed model
OLLAMA_TEMPERATURE = 0.0

# Logging Configuration
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
LOG_LEVEL = 'INFO'  # Set to 'DEBUG' for more verbosity
