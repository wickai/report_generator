from typing import Dict, Type, List
from .base import BaseAIModel
from .openai_model import OpenAIModel
from .gemini_model import GeminiModel
from .deepseek_model import DeepSeekModel

class AIModelFactory:
    _models: Dict[str, Type[BaseAIModel]] = {
        "openai": OpenAIModel,
        "gemini": GeminiModel,
        "deepseek": DeepSeekModel
    }

    _provider_models = {
        "openai": ["gpt-4o-mini", "gpt-4o", "o1", "o3-mini", "o1-mini",
                  "gpt-3.5-turbo", "gpt-3.5-turbo-instruct", 
                  "gpt-3.5-turbo-16k-0613", "gpt-4"],
        "gemini": ["gemini-pro"],
        "deepseek": ["deepseek-chat", "deepseek-coder", "deepseek-reasoner"]
    }

    @classmethod
    def create_model(cls, provider: str, model_name: str = None) -> BaseAIModel:
        if provider not in cls._models:
            raise ValueError(f"不支持的AI提供商: {provider}")
        
        if model_name and model_name not in cls._provider_models.get(provider, []):
            raise ValueError(f"不支持的模型名称: {model_name}")
        
        model_class = cls._models[provider]
        return model_class(model_name) if model_name else model_class()

    @classmethod
    def get_provider_models(cls, provider: str = None) -> Dict[str, List[str]]:
        if provider:
            if provider not in cls._provider_models:
                raise ValueError(f"不支持的AI提供商: {provider}")
            return {provider: cls._provider_models[provider]}
        return cls._provider_models