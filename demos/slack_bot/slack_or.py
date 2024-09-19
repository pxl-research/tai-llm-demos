import json
import os

from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from demos.components.open_router_client import OpenRouterClient, GPT_4O_MINI

load_dotenv()

# OpenRouter
or_client = OpenRouterClient(model_name=GPT_4O_MINI,
                             api_key=os.getenv('OPENROUTER_API_KEY'))

system_instruction = {
    'role': 'system',
    'content': 'I would like you to take a deep breath before responding.'
               'Always think step by step.'
               'Try to be concise, but precise as well.'
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
    response = or_client.create_completions_stream(message_list=history_openai_format, stream=False)
    response_text = response.choices[0].message.content

    say(f'{response_text}')  # respond to the command


if __name__ == '__main__':
    handler = SocketModeHandler(app, os.environ.get('SLACK_APP_TOKEN'))
    handler.start()
