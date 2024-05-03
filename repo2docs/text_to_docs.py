import os
from dotenv import load_dotenv
from repo2docs.llm import OpenAIClient, AnthropicClient, LLMClient
from repo2docs.prompts import documentation_prompt, diagram_prompt, database_prompt

load_dotenv()

class TextToDocs:
    def __init__(self, api_choice, model=None):
        if api_choice == "anthropic":
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                api_key = LLMClient.get_api_key('ANTHROPIC_API_KEY', 'Anthropic')
            self.client = AnthropicClient(api_key=api_key, model=model)
        elif api_choice == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                api_key = LLMClient.get_api_key('OPENAI_API_KEY', 'OpenAI')
            self.client = OpenAIClient(api_key=api_key, model=model)
        else:
            raise ValueError("Invalid API choice. Please choose either 'anthropic' or 'openai'.")
        
    def generate_docs(self, repo_txt, doc_type="documentation", prompt=None):
        """Generate documentation from the text based on the specified doc_type or prompt."""
        prompt_map = {
            "documentation": documentation_prompt,
            "diagram": diagram_prompt,
            "database": database_prompt
        }
        
        if prompt:
            selected_prompt = prompt
        elif doc_type in prompt_map:
            selected_prompt = prompt_map[doc_type]
        else:
            raise ValueError(f"Invalid doc_type: {doc_type}. Please choose from: {', '.join(prompt_map.keys())}")
        
        response = self.client.generate_response(
            prompt=selected_prompt,
            messages=[{"role": "user", "content": repo_txt}],
        )
        return response