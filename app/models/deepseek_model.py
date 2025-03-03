from typing import List, Dict
from openai import OpenAI
from .base import BaseAIModel
import os

class DeepSeekModel(BaseAIModel):
    def __init__(self, model_name: str = "deepseek-chat"):
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        self.model_name = model_name
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.deepseek.com"
        )

    async def generate_response(self, messages: List[Dict[str, str]]) -> str:
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            stream=False
        )
        
        return response.choices[0].message.content