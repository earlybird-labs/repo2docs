import os
from dotenv import load_dotenv
from repo2docs.llm import OpenAIClient, AnthropicClient, LLMClient
from repo2docs.prompts import documentation_prompt, diagram_prompt, mobile_prompt, database_prompt

load_dotenv()

class TextToDocs:
    def __init__(self, api_choice, model=None):
        if api_choice == "anthropic":
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                api_key = LLMClient.get_api_key('ANTHROPIC_API_KEY', 'Anthropic')
            self.client = AnthropicClient(api_key=api_key)
        elif api_choice == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                api_key = LLMClient.get_api_key('OPENAI_API_KEY', 'OpenAI')
            self.client = OpenAIClient(api_key=api_key)
        else:
            raise ValueError("Invalid API choice. Please choose either 'anthropic' or 'openai'.")
        
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

