import json
import os

from dotenv import load_dotenv
from openai import AzureOpenAI
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

load_dotenv()

# Azure Open AI
client = AzureOpenAI(
    api_key=os.getenv('AOA_API_KEY'),
    api_version='2024-02-15-preview',
    azure_endpoint=os.getenv('AOA_ENDPOINT'),
)

system_instruction = {
    'role': 'system',
    'content': 'You are a helpful assistant in a Slack workspace. '
               'Always think step by step. '
               'Be concise, but include all relevant details.'
}

# initializes Slack app
app = App(token=os.environ.get('SLACK_BOT_TOKEN'))


# Listens to incoming slash commands '/llm'
@app.command('/llm')
def handle_command(ack, say, command):
    print(json.dumps(command, indent=1))
    ack()  # acknowledge the command request

    history_openai_format = [
        system_instruction,
        {'role': 'user', 'content': command['text']}
    ]
    response = client.chat.completions.create(model='gpt-4o-mini',
                                              messages=history_openai_format,
                                              temperature=1.0)
    response_text = response.choices[0].message.content

    say(f'{response_text}')  # respond to the command


if __name__ == '__main__':
    handler = SocketModeHandler(app, os.environ.get('SLACK_APP_TOKEN'))
    handler.start()
