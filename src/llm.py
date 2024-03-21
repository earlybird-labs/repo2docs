from abc import ABC, abstractmethod
import os
import openai
import anthropic

class LLMClient(ABC):
    """
    Abstract base class for LLM clients.
    """
    @abstractmethod
    def generate_response(self, prompt, model, max_tokens, temperature, messages):
        pass

class OpenAIClient(LLMClient):
    def __init__(self, api_key):
        self.client = openai.OpenAI(api_key=api_key)

    def generate_response(self, prompt, model="gpt-4-turbo-preview", max_tokens=3000, temperature=0.5, messages=[]):
        response = self.client.chat.completions.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[
                {"role": "system", "content": prompt},
                *messages
            ]
        )
        return response.choices[0].message.content

class AnthropicClient(LLMClient):
    def __init__(self, api_key):
        self.client = anthropic.Anthropic(api_key=api_key)

    def generate_response(self, prompt, model="claude-3-sonnet-20240229", max_tokens=3000, temperature=0.5, messages=[]):
        response = self.client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=prompt,
            messages=messages
        )
        return response.content[0].text