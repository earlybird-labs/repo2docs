from abc import ABC, abstractmethod
import os
import openai
import anthropic
import sys
import getpass

class LLMClient(ABC):
    """
    Abstract base class for LLM clients.
    """

    @abstractmethod
    def generate_response(self, prompt, model, max_tokens, temperature, messages):
        pass

    @staticmethod
    def get_api_key(env_var, client_name):
        """
        Retrieve API key from environment or prompt user if not found, specifying the client.
        """
        api_key = os.getenv(env_var)
        if not api_key:
            print(f"API key for {client_name} ({env_var}) not found. Please enter your API key:")
            api_key = getpass.getpass(prompt='')
        return api_key

class OpenAIClient(LLMClient):
    def __init__(self, api_key: str = None, model: str = None):
        if not api_key:
            api_key = self.get_api_key('OPENAI_API_KEY', 'OpenAI')
        if model is None:
            model = 'gpt-4-turbo'
        self.model = model
        self.client = openai.OpenAI(api_key=api_key)
        

    def generate_response(
        self,
        prompt,
        max_tokens=4000,
        temperature=0.5,
        messages=[],
    ):
        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[{"role": "system", "content": prompt}, *messages],
        )
        return response.choices[0].message.content


class AnthropicClient(LLMClient):
    def __init__(self, api_key: str = None, model: str = None):
        if not api_key:
            api_key = self.get_api_key('ANTHROPIC_API_KEY', 'Anthropic')
        if model is None:
            model = 'claude-3-haiku-20240307'
        self.model = model
        self.client = anthropic.Anthropic(api_key=api_key)

    def generate_response(
        self,
        prompt,
        max_tokens=4000,
        temperature=0.5,
        messages=[],
    ):
        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=prompt,
            messages=messages,
        )
        return response.content[0].text