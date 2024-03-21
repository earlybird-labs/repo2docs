import os
from dotenv import load_dotenv
import anthropic
from prompt_loader import load_prompt

load_dotenv()

class TextToDocs:
    """A class to convert text to documentation using the Anthropic API."""

    def __init__(self):
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    def generate_docs(self, repo_txt):
        """Generate documentation from the text."""
        documentation_prompt = load_prompt("documentation.txt")

        response = self.client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=4000,
            temperature=0.4,
            system=documentation_prompt,
            messages=[
                {"role": "user", "content": repo_txt}
            ]
        )
        return response.content[0].text
    
    def generate_diagram(self, repo_txt):
        """Generate a diagram from the text."""
        diagram_prompt = load_prompt("diagrams.txt")

        response = self.client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=4000,
            temperature=0.6,
            system=diagram_prompt,
            messages=[
                {"role": "user", "content": repo_txt}
            ]
        )
        return response.content[0].text


