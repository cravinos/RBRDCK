# prompts/prompt_templates.py
from typing import Dict, List
from IPython.display import display, Markdown
import markdown

def create_review_prompt(diff: str, previous_comments: str) -> str:
    """
    Creates a prompt for a code review with interactive elements for suggesting changes.

    Args:
    diff (str): The diff string representing changes in the pull request.
    previous_comments (str): A string containing previous comments on the pull request.

    Returns:
    str: A formatted prompt string for code review with interactive elements.
    """
    prompt = f"""
    You are now a Code Review Engineer AI, designed to enhance software quality and development practices. Here's what you need to do:

    **Review Objectives:**
    - **Code Quality**: Assess for clarity, efficiency, and maintainability.
    - **Bug Detection**: Identify potential bugs or logical errors.
    - **Standards Compliance**: Verify if the code adheres to the project's coding standards.
    - **Improvement Suggestions**: Recommend enhancements or optimizations.

    **Context:**
    Previous comments on this pull request:
    {previous_comments}

    Please take these previous comments into account when conducting your review.

    **Interactive Review Process:**
    - Review the code diff provided below.
    - For each point of feedback, consider if a code change could improve the situation.
    - If so, provide your suggestions using GitHub's suggestion block:

    ```suggestion
    <your code suggestion here>
    ```

    Actionable Feedback:
    After your suggestions, there will be a button labeled "Apply Suggestions to PR". 
    When clicked, your code suggestions will be proposed as changes to the pull request.

    Code Diff for Review:

    {diff}

    Instructions:
    Deliver your analysis in Markdown bullet points for readability.
    Be precise with line numbers when referencing changes or issues.
    When suggesting code, ensure it's within the context of the existing code to maintain coherence.
    Address any concerns or points raised in the previous comments.

    Please proceed with your review."""

    return prompt

def create_documentation_review_prompt(diff: str, previous_comments: str) -> str:
    """
    Creates a prompt for documentation review.

    Args:
    diff (str): The diff string representing changes in the pull request.
    previous_comments (str): A string containing previous comments on the pull request.

    Returns:
    str: A formatted prompt string for documentation review.
    """
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

def create_code_quality_prompt(diff: str, previous_comments: str, analysis: Dict) -> str:
    """
    Creates a prompt for code quality review.

    Args:
    diff (str): The diff string representing changes in the pull request.
    previous_comments (str): A string containing previous comments on the pull request.
    analysis (Dict): Dictionary containing code quality analysis results.

    Returns:
    str: A formatted prompt string for code quality review.
    """
    prompt = f"""
    You are an expert code reviewer. Your task is to analyze code changes for quality and suggest improvements.

    **Code Analysis:**
    Files Changed: {analysis.get('summary', {}).get('files_changed', 0)}
    Total Lines Changed: {analysis.get('summary', {}).get('total_lines_changed', 0)}
    Average Complexity: {analysis.get('summary', {}).get('average_complexity', 0)}
    High Complexity Files: {analysis.get('summary', {}).get('high_complexity_files', 0)}

    **Files Changed:**
    {diff}

    **Context:**
    Previous comments on this pull request:
    {previous_comments}

    **Instructions:**
    1. Review the code changes and analysis results
    2. Identify:
       - Code quality issues
       - Potential bugs
       - Performance concerns
       - Style inconsistencies
    3. Provide specific suggestions using code blocks
    4. Prioritize feedback based on severity

    Please provide your review below:
    """
    return prompt