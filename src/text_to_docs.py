import os
from dotenv import load_dotenv
from prompt_loader import load_prompt
from llm import OpenAIClient, AnthropicClient

load_dotenv()

class TextToDocs:
    """A class to convert text to documentation using a language model API."""

    def __init__(self, api_choice):
        api_key = os.getenv(f"{api_choice.upper()}_API_KEY")
        if api_choice == "anthropic":
            self.client = AnthropicClient(api_key=api_key)
        elif api_choice == "openai":
            self.client = OpenAIClient(api_key=api_key)
        else:
            raise ValueError("Invalid API choice. Please choose either 'anthropic' or 'openai'.")

    def generate_docs(self, repo_txt):
        """Generate documentation from the text."""
        documentation_prompt = load_prompt("documentation.txt")
        response = self.client.generate_response(
            prompt=documentation_prompt,
            messages=[{"role": "user", "content": repo_txt}]
        )
        return response
    
    def generate_diagram(self, repo_txt):
        """Generate a diagram from the text."""
        diagram_prompt = load_prompt("diagrams.txt")
        response = self.client.generate_response(
            prompt=diagram_prompt,
            messages=[{"role": "user", "content": repo_txt}]
        )
        return response

