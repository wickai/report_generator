from typing import List, Dict
from openai import OpenAI
from .base import BaseAIModel
import os

class OpenAIModel(BaseAIModel):
    VALID_MODELS = {
        "gpt-4o-mini", "gpt-4o", "o1", "o3-mini", "o1-mini",
        "gpt-3.5-turbo", "gpt-3.5-turbo-instruct", "gpt-3.5-turbo-16k-0613",
        "gpt-4"
    }

    def __init__(self, model_name: str = "gpt-4"):
        if model_name not in self.VALID_MODELS:
            raise ValueError(f"Invalid model name. Must be one of: {', '.join(sorted(self.VALID_MODELS))}")
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model_name = model_name

    async def generate_response(self, messages: List[Dict[str, str]]) -> str:
        completion = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages
        )
        return completion.choices[0].message.content