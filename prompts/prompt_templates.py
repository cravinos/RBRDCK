# prompts/prompt_templates.py

def create_review_prompt(diff: str) -> str:
    prompt = f"""
You are an experienced software engineer tasked with reviewing a pull request. Analyze the following code changes and provide constructive feedback focusing on:

- Code quality and readability
- Potential bugs or issues
- Adherence to coding standards and best practices
- Suggestions for improvements

Here are the code changes:

{diff}

Please provide your feedback in clear, concise bullet points formatted in Markdown.
"""
    return prompt
