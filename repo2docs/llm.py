from abc import ABC, abstractmethod
import openai
import anthropic

from repo2docs.utils import get_api_key

client_models = {
    "openai": ["gpt-4-turbo", "gpt-3.5-turbo"],
    "anthropic": [
        "claude-3-haiku-20240307",
        "claude-3-sonnet-20240229",
        "claude-3-opus-20240229",
    ],
}


class LLMClient(ABC):
    @abstractmethod
    def generate_response(self, prompt, model, max_tokens, temperature, messages):
        pass


class OpenAIClient(LLMClient):
    def __init__(self, api_key: str = None, model: str = None):
        if not api_key:
            api_key = get_api_key("OPENAI_API_KEY", "OpenAI")
        self.model = model or "gpt-4-turbo"
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
            api_key = self.get_api_key("ANTHROPIC_API_KEY", "Anthropic")
        self.model = model or "claude-3-haiku-20240307"
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
