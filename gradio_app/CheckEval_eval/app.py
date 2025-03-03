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

def generate_prompt(aspect, definition, source, report, questions):
    prompt = f"""In this task, you will be provided with a 7 days energy data and a data report. Your task is to answer 'Yes' or 'No' to the questions related to the {aspect}. Do not generate any explanations without answer to the questions.
Please make sure you read and understand these instructions carefully. Please keep this document open while reviewing, and refer to it as needed.

Evaluation Criteria: 
{aspect} - {definition}

Evaluation Steps:
1. Analyze the summary to evaluate {aspect}.
2. Respond to each of the following questions with either 'Yes' or 'No' to evaluate the {aspect}. 
3. Please answer 'Yes' or 'No'. No need to any explain.

7 Days Energy Data: {source}

Data Report: {report}
Questions:
"""
    question_lines = questions.strip().split('\n')
    for line in question_lines:
        if line.strip():
            prompt += f"- {line}\n"
    
    prompt += "\nYour Answers:"
    return prompt

def evaluate(aspect, definition, source, report, questions, provider, model, history):
    try:
        prompt = generate_prompt(aspect, definition, source, report, questions)
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
with gr.Blocks(title="报告评估器") as demo:
    gr.Markdown("# 报告评估器")
    
    with gr.Row():
        with gr.Column(scale=4):
            chatbot = gr.Chatbot(height=600)
            with gr.Row():
                copy_btn = gr.Button("复制原始回答")
            raw_output = gr.Textbox(label="原始回答", visible=True)
            
            with gr.Row():
                submit = gr.Button("评估")
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
            )
            source = gr.Textbox(
                label="数据源 (Source)",
                placeholder="输入原始数据...",
                lines=5,
                value="""REGIONID,DATATYPE,DATAVALUE,CALENDAR_DATE,PRETTYDATE
NSW1,Net Interchange,-1875,2024/09/26 00:00:00,26-Sep-24
NSW1,Scheduled Capacity,9454,2024/09/26 00:00:00,26-Sep-24
NSW1,Scheduled Demand,9776,2024/09/26 00:00:00,26-Sep-24"""
            )
            report = gr.Textbox(
                label="报告内容 (Report)",
                placeholder="输入报告内容...",
                lines=5,
                value="""根据提供的数据，可以看出以下关键信息：

1. 数据涉及的区域包括NSW1、QLD1、SA1、TAS1、VIC1。
2. 数据类型包括净互换（Net Interchange）、计划容量（Scheduled Capacity）、计划需求（Scheduled Demand）、计划储备（Scheduled Reserve）、交易间隔（Trading Interval）。
3. 数据值范围从负数到正数不等，反映了不同类型数据的变化情况。
4. 数据日期从2024年9月26日到2024年10月2日，每日都有对应的数据记录。
5. 不同区域和不同数据类型的数据值存在差异，反映了不同区域的能源交易情况和需求情况。
6. 数据值的变化反映了不同区域在不同日期的能源供需状况。
7. 不同区域和不同数据类型的交易间隔也有差异，体现了不同区域的能源交易方式和时间安排。"""
            )
            questions = gr.Textbox(
                label="评估问题 (Questions)",
                placeholder="每行输入一个问题...",
                lines=5,
                value="""Does the report include all relevant power data?
Are there any important pieces of power data that are missing from the report?
Has all the power data been clearly presented in the report?
Is there any critical information about power data that has been omitted?"""
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
        inputs=[aspect, definition, source, report, questions, provider, model, chatbot],
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