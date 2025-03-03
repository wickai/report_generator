from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import List, Optional
from app.models.factory import AIModelFactory
import os

# 加载环境变量
load_dotenv()

# 创建FastAPI应用
app = FastAPI()

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    provider: str
    model_name: Optional[str] = None
    message: str

@app.post("/chat")
async def chat_with_ai(request: ChatRequest):
    try:
        # 创建对应的AI模型实例
        ai_model = AIModelFactory.create_model(request.provider, request.model_name)
        
        # 准备消息
        messages = [{"role": "user", "content": request.message}]
        
        # 生成响应
        response = await ai_model.generate_response(messages)
        
        return {
            "status": "success",
            "provider": request.provider,
            "model": request.model_name,
            "message": response
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/providers")
async def get_available_providers():
    return {
        "providers": list(AIModelFactory._models.keys())
    }

@app.get("/models/{provider}")
async def get_provider_models(provider: str):
    try:
        return AIModelFactory.get_provider_models(provider)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/models")
async def get_all_models():
    return AIModelFactory.get_provider_models()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)