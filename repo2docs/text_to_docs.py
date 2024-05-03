import os
from dotenv import load_dotenv
from repo2docs.llm import OpenAIClient, AnthropicClient
from repo2docs.prompts import documentation_prompt, diagram_prompt, mobile_prompt, database_prompt

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
            raise ValueError(
                "Invalid API choice. Please choose either 'anthropic' or 'openai'."
            )

    def generate_docs(self, repo_txt):
        """Generate documentation from the text."""
        response = self.client.generate_response(
            prompt=documentation_prompt,
            messages=[{"role": "user", "content": repo_txt}],
        )
        return response

    def generate_diagram(self, repo_txt):
        """Generate a diagram from the text."""
        response = self.client.generate_response(
            prompt=diagram_prompt, messages=[{"role": "user", "content": repo_txt}]
        )
        return response

    def generate_mobile(self, repo_txt):
        """Generate a mobile application documentation from the text."""
        response = self.client.generate_response(
            prompt=mobile_prompt, messages=[{"role": "user", "content": repo_txt}]
        )
        return response

    def generate_database(self, repo_txt):
        """Generate a database ERD from the text."""
        response = self.client.generate_response(
            prompt=database_prompt, messages=[{"role": "user", "content": repo_txt}]
        )
        return response

    def generate_custom(self, repo_txt, prompt):
        """Generate a custom documentation from the text."""
        response = self.client.generate_response(
            prompt=prompt, messages=[{"role": "user", "content": repo_txt}]
        )
        return response

