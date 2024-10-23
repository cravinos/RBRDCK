# agents/documentation_review_agent.py
from github.PullRequest import PullRequest

from llm.ollama_llm import OllamaLLM
import logging

logger = logging.getLogger(__name__)

class DocumentationReviewAgent:
    def __init__(self):
        self.llm = OllamaLLM()

    def review_documentation(self, diff: str, previous_comments: str) -> str:
        prompt = self.create_documentation_prompt(diff, previous_comments)
        try:
            response = self.llm.call(prompt)
            if not response.strip():
                logger.error("Empty documentation review generated.")
                return "Error: Documentation review returned an empty response."
            return response
        except Exception as e:
            logger.error(f"Error generating documentation review: {e}", exc_info=True)
            return f"Error generating documentation review: {str(e)}"

    def create_documentation_prompt(self, diff: str, previous_comments: str) -> str:
        prompt = f"""
        You are an expert documentation reviewer. Your task is to ensure that all code changes are properly documented.

        **Review Objectives:**
        - **Inline Comments:** Check if new or modified code includes appropriate inline comments.
        - **README Updates:** Ensure that the README file is updated to reflect significant changes or new features.
        - **Documentation Standards:** Verify adherence to the project's documentation standards and guidelines.

        **Context:**
        Previous comments on this pull request:
        {previous_comments}

        **Code Diff for Documentation Review:**
        {diff}

        **Instructions:**
        - Identify areas where documentation is lacking or could be improved.
        - Provide specific suggestions for enhancing documentation.
        - Use GitHub's suggestion block for code/documentation changes.

        Please provide your review below:
        """
        return prompt
