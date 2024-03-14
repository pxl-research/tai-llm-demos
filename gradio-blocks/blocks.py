import random
import time

import gradio as gr


def respond(message, chat_history):
    bot_message = random.choice(["How are you?", "I love you", "I'm very hungry"])
    chat_history.append((message, bot_message))
    time.sleep(0.5)
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
