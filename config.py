# config.py

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# GitHub Configuration
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_USER = "cravinos"  # User will for now manually type it 
REPO_OWNER = 'cravinos'
#REPO_NAME = # this needs to be relative to the PR the user is clicking on so we need to get rid of it here  
GITHUB_API_URL = "https://api.github.com"
FRONTEND_URL = "http://localhost:3000"

# LLM Configuration
OLLAMA_BASE_URL = "http://localhost:11434"  # Update if necessary
OLLAMA_MODEL = "llama3:latest"  # Replace with your installed model
OLLAMA_TEMPERATURE = 0.0

# Logging Configuration
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
LOG_LEVEL = 'INFO'  # Set to 'DEBUG' for more verbosity
