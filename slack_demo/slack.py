import os

from dotenv import load_dotenv
from openai import AzureOpenAI
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

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

# initializes slack app
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))


# Listens to incoming slash commands "/llm"
@app.command("/llm")
def handle_command(ack, say, command):
    # Acknowledge the command request
    ack()
    history_openai_format = [system_instruction]
    history_openai_format.append({"role": "user", "content": command['text']})

    response = client.chat.completions.create(model='gpt-4-turbo-04-09',
                                              messages=history_openai_format,
                                              temperature=1.0)
    response_text = response.choices[0].message.content
    print(response_text)

    # Respond to the command
    say(f"{response_text}")


if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN"))
    handler.start()
