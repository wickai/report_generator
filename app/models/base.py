from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseAIModel(ABC):
    @abstractmethod
    async def generate_response(self, messages: List[Dict[str, str]]) -> str:
        """生成AI响应的抽象方法"""
        pass 