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


def respond(message, chat_history):
    chat_history.append((message, None))

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
        time.sleep(5)
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        print("Elapsed time: {} minutes {} seconds".format(int((time.time() - start_time) // 60),
                                                           int((time.time() - start_time) % 60)))
        status = run.status
        print(f'Status: {status}')

    print(f'Status: {status}')
    print("Elapsed time: {} minutes {} seconds".format(int((time.time() - start_time) // 60),
                                                       int((time.time() - start_time) % 60)))

    messages = client.beta.threads.messages.list(
        thread_id=thread.id
    )
    print(messages.model_dump_json(indent=2))

    bot_message = ""
    for msgData in messages.data:
        if msgData.role == "assistant" and msgData.content[0].type == "text":
            bot_message = msgData.content[0].text.value
            break
    chat_history.append((None, bot_message))

    return "", chat_history


# https://www.gradio.app/guides/creating-a-custom-chatbot-with-blocks
with gr.Blocks() as blocks_ui:
    # UI composition
    chatbot = gr.Chatbot(label='Log')
    with gr.Row():
        msg = gr.Textbox(label='Prompt', scale=1)
        send = gr.Button('Send', scale=0)
    clear = gr.ClearButton([msg, chatbot])

    # event handlers
    msg.submit(respond, [msg, chatbot], [msg, chatbot])
    send.click(respond, [msg, chatbot], [msg, chatbot])

blocks_ui.launch()
