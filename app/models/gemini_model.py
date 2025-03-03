from typing import List, Dict
import google.generativeai as genai
from .base import BaseAIModel
import os

class GeminiModel(BaseAIModel):
    def __init__(self, model_name: str = "gemini-pro"):
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.model = genai.GenerativeModel(model_name)

    async def generate_response(self, messages: List[Dict[str, str]]) -> str:
        # 将消息格式转换为Gemini支持的格式
        chat = self.model.start_chat()
        response = chat.send_message(messages[-1]["content"])  # 这里简化处理，只取最后一条消息
        return response.text 