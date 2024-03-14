import json
import gradio as gr
import tiktoken
import os

from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()

client = AzureOpenAI(
    api_key=os.getenv("AOA_API_KEY"),
    api_version="2024-02-15-preview",
    azure_endpoint=os.getenv("AOA_ENDPOINT"),
)

system_instruction = {
    "role": "system",
    "content": "I would like you to take a deep breath before responding."
               "Always think step by step."
               "Try to be concise, but precise as well."
}


def predict(message, history):
    tokeniser = tiktoken.encoding_for_model("gpt-4")

    msg_len = len(tokeniser.encode(message))
    print(f"Message: {message} ({msg_len} tokens)")

    history_openai_format = [system_instruction]  # openai format

    for human, assistant in history:
        history_openai_format.append({"role": "user", "content": human})
        history_openai_format.append({"role": "assistant", "content": assistant})
    history_openai_format.append({"role": "user", "content": message})

    hist_string = json.dumps(history_openai_format)
    hist_len = len(tokeniser.encode(hist_string))
    print(f"History: {hist_len} tokens")
    cost_in_cents = round(hist_len / 1000 * 3)
    if cost_in_cents > 0:
        print(f"Cost estimate: {cost_in_cents} cents")

    response_stream = client.chat.completions.create(model='gpt-4-1106-preview',
                                                     messages=history_openai_format,
                                                     temperature=1.0,
                                                     stream=True)
    partial_message = ""
    for chunk in response_stream:
        if len(chunk.choices) > 0 and chunk.choices[0].delta.content is not None:
            partial_message = partial_message + chunk.choices[0].delta.content
            yield partial_message


gr.ChatInterface(predict).launch()
