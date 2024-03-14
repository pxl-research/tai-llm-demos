import os
import time

import gradio as gr
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()

client = AzureOpenAI(
    api_key=os.getenv("AOA_API_KEY"),
    api_version="2024-02-15-preview",
    azure_endpoint=os.getenv("AOA_ENDPOINT"),
)

general_instructions = ("I would like you to take a deep breath before responding."
                        "Always think step by step."
                        "Try to be concise, but precise as well.")

assistant = client.beta.assistants.create(
    name="Professional Assistant",
    description="You support a team of applied researchers operating in Europe.",
    instructions=general_instructions,
    model="gpt-4-1106-preview",
    tools=[{"type": "code_interpreter"}],
)

thread = client.beta.threads.create()


def clear_log():
    global thread
    thread = client.beta.threads.create()
    return ["", ""]


def append_user(message, chat_history):
    chat_history.append((message, None))
    return chat_history


def append_ai(message, chat_history):
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=message
    )

    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
    )

    start_time = time.time()
    status = run.status
    while status not in ["completed", "cancelled", "expired", "failed"]:
        time.sleep(0.25)
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        time_diff = int((time.time() - start_time))
        status = run.status
        print(f"Elapsed time: {time_diff} seconds, Status: {status}")

    if run.usage:
        print(f"Tokens {run.usage.prompt_tokens} (prompt) and {run.usage.completion_tokens} (response)")

    messages = client.beta.threads.messages.list(
        thread_id=thread.id
    )

    bot_message = ""
    for msgData in messages.data:
        if msgData.role == "assistant" and msgData.content[0].type == "text":
            bot_message = msgData.content[0].text.value
            break
    chat_history.append((None, bot_message))

    return "", chat_history


# https://www.gradio.app/guides/creating-a-custom-chatbot-with-blocks
with gr.Blocks(fill_height=True) as blocks_ui:
    # UI composition
    tb_log = gr.Chatbot(label='Log', scale=1)
    with gr.Row():
        tb_user = gr.Textbox(label='Prompt', scale=1)
        btn_send = gr.Button('Send', scale=0)
    btn_clear = gr.Button('Clear')

    # event handlers
    tb_user.submit(append_user, [tb_user, tb_log], [tb_log]
                   ).then(append_ai, [tb_user, tb_log], [tb_user, tb_log])
    btn_send.click(append_user, [tb_user, tb_log], [tb_log]
                   ).then(append_ai, [tb_user, tb_log], [tb_user, tb_log])
    btn_clear.click(clear_log, None, [tb_user, tb_log])

blocks_ui.launch()
