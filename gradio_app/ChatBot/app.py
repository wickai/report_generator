import gradio as gr
import requests

API_BASE_URL = "http://localhost:8000"

def get_providers():
    try:
        response = requests.get(f"{API_BASE_URL}/providers")
        if response.status_code == 200:
            return response.json()["providers"]
        return []
    except:
        return []

def get_models(provider):
    try:
        response = requests.get(f"{API_BASE_URL}/models/{provider}")
        if response.status_code == 200:
            return response.json()[provider]
        return []
    except:
        return []

def chat(message, provider, model, history):
    try:
        response = requests.post(
            f"{API_BASE_URL}/chat",
            json={
                "provider": provider,
                "model_name": model,
                "message": message
            }
        )
        if response.status_code == 200:
            raw_message = response.json()['message']
            bot_message = f"[{provider} {model}]\n{raw_message}"
        else:
            bot_message = f"错误: {response.text}"
            raw_message = ""
    except Exception as e:
        bot_message = f"请求失败: {str(e)}"
        raw_message = ""
    
    history.append((message, bot_message))
    return "", history, raw_message

def update_models(provider):
    models = get_models(provider)
    return gr.Dropdown(choices=models, value=models[0] if models else None)

def initialize_providers_and_models():
    providers = get_providers()
    if not providers:
        return ["无可用提供商"], []
    
    initial_models = get_models(providers[0])
    return providers, initial_models

# 获取可用的AI提供商和初始模型
providers, initial_models = initialize_providers_and_models()

# 创建Gradio界面
with gr.Blocks(title="AI 聊天助手") as demo:
    gr.Markdown("# AI 聊天助手")
    
    with gr.Row():
        with gr.Column(scale=4):
            chatbot = gr.Chatbot(height=600)
            with gr.Row():
                msg = gr.Textbox(label="在这里输入您的问题...", placeholder="请输入您的问题", scale=4)
                copy_btn = gr.Button("复制原始回答", scale=1)
            with gr.Row():
                submit = gr.Button("发送")
                clear = gr.Button("清除对话")
            raw_output = gr.Textbox(label="原始回答", visible=True)  # 改为可见
        
        with gr.Column(scale=1):
            provider = gr.Dropdown(
                choices=providers,
                value=providers[0] if providers else None,
                label="选择AI提供商"
            )
            model = gr.Dropdown(
                choices=initial_models,
                value=initial_models[0] if initial_models else None,
                label="选择模型"
            )

    provider.change(
        update_models,
        inputs=[provider],
        outputs=[model]
    )

    submit.click(
        chat,
        inputs=[msg, provider, model, chatbot],
        outputs=[msg, chatbot, raw_output]
    )
    
    def copy_last_response(history):
        if history and len(history) > 0:
            last_response = history[-1][1]
            if '\n' in last_response:
                raw_text = last_response.split('\n', 1)[1]
                return gr.update(value=raw_text)
        return gr.update(value="")
    
    copy_btn.click(
        copy_last_response,
        inputs=[chatbot],
        outputs=[raw_output],
    )

    # 添加 JavaScript 复制功能
    raw_output.change(
        None,
        None,
        None,
        js="""
        () => {
            const text = document.querySelector('#component-43').querySelector('textarea').value;
            navigator.clipboard.writeText(text);
        }
        """
    )

    clear.click(lambda: (None, ""), None, [chatbot, raw_output], queue=False)

demo.launch(share=False)