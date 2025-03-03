# report_generator
A specific domain report generator

# AI 模型统一调用接口

这是一个统一的AI模型调用接口，支持多个AI提供商的API调用，包括OpenAI、Google Gemini和DeepSeek等。

## 功能特点

- 支持多个AI提供商的API调用
- 统一的接口格式
- 可扩展的模块化设计
- RESTful API设计
- 异步处理请求

## 支持的AI提供商

- OpenAI (GPT-4, GPT-3.5等)
- Google Gemini
- DeepSeek
- 更多提供商持续添加中...

## 环境要求

- Python 3.8+
- FastAPI
- uvicorn
- openai
- google-generativeai
- python-dotenv
- requests

## 安装步骤

1. 克隆项目

2. 安装依赖

```
pip install fastapi uvicorn openai google-generativeai python-dotenv requests
```

3. 配置环境变量
创建 `.env` 文件并添加以下内容：
```
OPENAI_API_KEY=你的OpenAI_API密钥
GOOGLE_API_KEY=你的Google_API密钥
DEEPSEEK_API_KEY=你的DeepSeek_API密钥
```
## 启动服务

python main.py

服务将在 http://localhost:8000 启动

## API 使用说明

### 1. 获取支持的AI提供商列表
bash
curl http://localhost:8000/providers

### 2. 发送聊天请求

bash
curl -X POST http://localhost:8000/chat \
-H "Content-Type: application/json" \
-d '{
"provider": "openai",
"model_name": "gpt-4",
"message": "你好，请介绍一下你自己"
}'

请求参数说明：
- provider: AI提供商名称（必填）
- model_name: 模型名称（可选）
- message: 用户消息内容（必填）

### 3. 各提供商支持的模型

#### OpenAI
- gpt-4
- gpt-3.5-turbo
- 等其他OpenAI支持的模型

#### Google Gemini
- gemini-pro
- 其他Gemini支持的模型

#### DeepSeek
- deepseek-chat
- 其他DeepSeek支持的模型

## API 响应示例

json
{
"status": "success",
"provider": "openai",
"model": "gpt-4",
"message": "AI的响应内容"
}

## 错误处理

服务会返回适当的HTTP状态码和错误信息：
- 400: 请求参数错误
- 500: 服务器内部错误
- 其他特定错误码

## 开发扩展

要添加新的AI提供商支持，需要：

1. 在 `app/models` 目录下创建新的模型类
2. 继承 `BaseAIModel` 类并实现必要的方法
3. 在 `AIModelFactory` 中注册新的模型

## 注意事项

- 在生产环境中请确保正确设置CORS和安全措施
- 请妥善保管API密钥
- 建议设置请求速率限制
- 注意各AI提供商的使用条款和限制

## License

[您的许可证类型]