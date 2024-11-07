# config.py
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# GitHub Configuration
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
if not GITHUB_TOKEN:
    raise ValueError("GITHUB_TOKEN not found in environment variables")

# Logging Configuration
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# Integration Configuration
SLACK_WEBHOOK_URL = os.getenv('SLACK_WEBHOOK_URL')
JIRA_URL = os.getenv('JIRA_URL')
JIRA_USERNAME = os.getenv('JIRA_USERNAME')
JIRA_API_TOKEN = os.getenv('JIRA_API_TOKEN')

# LLM Configuration
OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'llama3:latest')
OLLAMA_TEMPERATURE = float(os.getenv('OLLAMA_TEMPERATURE', '0.2'))