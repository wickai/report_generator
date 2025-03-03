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

def generate_prompt(aspect, definition, components):
    prompt = f"""In this task, you need to create a question to evaluate the {aspect} of the summary of the original document. The definition of {aspect} and the questions corresponding to the key component of {aspect} are provided below. Use them to generate sub-questions for each key question.

Each sub-question must satisfy the following conditions:
1. Each question must be answerable with 'Yes' or 'No'.
2. Each question must contain concepts from the key component.
3. Each question should minimize the subjectivity of the rater's judgment.
4. Each question should minimize the semantic redundancy between sub-questions.
5. Formulate questions so that a 'Yes' answer is a positive answer.

# Definition
{aspect} - {definition}

# Key component and corresponding question
"""
    # 将components按行分割，并处理每一行
    component_lines = components.strip().split('\n')
    for line in component_lines:
        if line.strip():
            prompt += f"- {line}\n"
    
    prompt += "\nSub-questions:"
    print(f"prompt:{prompt}")
    return prompt

def evaluate(aspect, definition, components, provider, model, history):
    try:
        prompt = generate_prompt(aspect, definition, components)
        response = requests.post(
            f"{API_BASE_URL}/chat",
            json={
                "provider": provider,
                "model_name": model,
                "message": prompt
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
    
    history.append((prompt, bot_message))
    return history, raw_message

def update_models(provider):
    models = get_models(provider)
    return gr.Dropdown(choices=models, value=models[0] if models else None)

# 初始化提供商和模型
providers = get_providers()
if not providers:
    providers = ["无可用提供商"]
initial_models = get_models(providers[0]) if providers else []

# 创建Gradio界面
with gr.Blocks(title="评估问题生成器") as demo:
    gr.Markdown("# 评估问题生成器")
    
    with gr.Row():
        with gr.Column(scale=4):
            chatbot = gr.Chatbot(height=600)
            with gr.Row():
                copy_btn = gr.Button("复制原始回答")
            raw_output = gr.Textbox(label="原始回答", visible=True)
            
            with gr.Row():
                submit = gr.Button("生成")
                clear = gr.Button("清除")
        
        with gr.Column(scale=2):
            aspect = gr.Textbox(
                label="评估方面 (Aspect)",
                placeholder="例如: Content Completeness",
                value="Content Completeness"
            )
            definition = gr.Textbox(
                label="定义 (Definition)",
                placeholder="输入定义...",
                value="""refers to the extent to which a report includes all relevant information and addresses all key aspects of the topic without omitting important details. It ensures that the report provides a comprehensive and thorough analysis of the subject matter.""",
                # lines=2
            )
            components = gr.Textbox(
                label="关键组件 (Key Components)",
                placeholder="每行输入一个组件...",
                lines=5,
                value="""Data Completeness: Ensure that the report includes all relevant power data without omitting important information.
Analysis Completeness: Assess whether the report provides a comprehensive analysis of all relevant aspects without ignoring important factors.
Conclusion Completeness: Determine whether the conclusions in the report are comprehensive and consider all possible situations and influencing factors"""
            )
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
        evaluate,
        inputs=[aspect, definition, components, provider, model, chatbot],
        outputs=[chatbot, raw_output]
    )
    
    def copy_last_response(history):
        if history and len(history) > 0:
            last_response = history[-1][1]
            if '\n' in last_response:
                raw_text = last_response.split('\n', 1)[1]
                return raw_text
        return ""
    
    copy_btn.click(
        copy_last_response,
        inputs=[chatbot],
        outputs=[raw_output]
    )

    clear.click(lambda: (None, ""), None, [chatbot, raw_output], queue=False)

demo.launch(share=False)