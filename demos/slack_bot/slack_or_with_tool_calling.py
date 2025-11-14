import json
import os
import re

from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from demos.components.open_router.open_router_client import OpenRouterClient
from demos.tool_calling.tool_descriptors import (tools_rag_descriptor,
                                                 tools_search_descriptor,
                                                 tools_get_website_contents)
# noinspection PyUnresolvedReferences
from demos.tool_calling.tools_rag import lookup_in_documentation
# noinspection PyUnresolvedReferences
from demos.tool_calling.tools_search import search_on_google
# noinspection PyUnresolvedReferences
from demos.tool_calling.tools_surf import (get_webpage_content, get_webpage_with_js)

load_dotenv()

tool_list = tools_rag_descriptor
tool_list.append(tools_search_descriptor)
tool_list.extend(tools_get_website_contents)

# OpenRouter
or_client = OpenRouterClient(model_name='anthropic/claude-haiku-4.5',
                             tools_list=tool_list,
                             api_key=os.getenv('OPENROUTER_API_KEY'))

system_instruction = {
    'role': 'system',
    'content': 'You are a helpful assistant in a Slack workspace. '
               'Always think step by step. '
               'Be concise, but include all relevant details. Always think step by step. '
               'Try to complete your assignments in one go (i.e. do not ask for extra details). '
               'If information is missing, make reasonable assumptions and state them. '
               'Restate the user’s question before answering. '
               'Format your answer using Markdown for clarity. '
               'When using an external source, always include the reference.'
}

# initializes Slack app
app = App(token=os.environ.get('SLACK_BOT_TOKEN'))


# Listens to incoming slash commands '/llm'
@app.command('/llm')
def handle_command(ack, say, command):
    ack()  # acknowledge the command request
    print(f'Processing command: "{command['text']}"')

    history_openai_format = [
        system_instruction,
        {'role': 'user', 'content': command['text']}
    ]

    response = complete_with_llm(history_openai_format)
    if response:
        say(f'{response}')  # respond to the command
    else:
        say('Sorry, I can\'t help you with that...')  # respond to the command


def complete_with_llm(message_list):
    response = or_client.create_completions_stream(message_list=message_list, stream=False)

    message = response.choices[0].message
    if message.content is not None and message.content:
        slack_markup = convert_markdown_to_slack_markup(message.content)
        return f'{slack_markup}'
    if message.tool_calls is not None:
        return handle_tool_calls(message.tool_calls, message_list)
    else:
        print(response)
        return f'Failed to get a response...'


def handle_tool_calls(tool_calls, message_list):
    # handle tool requests
    if len(tool_calls) > 0:
        print(f'Processing {len(tool_calls)} tool calls')
        for call in tool_calls:
            fn_pointer = globals()[call.function.name]
            fn_args = json.loads(call.function.arguments)
            tool_call_obj = {
                'role': 'assistant',
                'content': None,
                'tool_calls': [
                    {
                        'id': call.id,
                        'type': 'function',
                        'function': {
                            'name': call.function.name,
                            'arguments': call.function.arguments
                        }
                    }
                ]
            }
            message_list.append(tool_call_obj)

            if fn_pointer is not None:
                fn_result = fn_pointer(**fn_args)
                tool_resp = {'role': 'tool',
                             'name': call.function.name,
                             'tool_call_id': call.id,
                             'content': json.dumps(fn_result)}
                message_list.append(tool_resp)

        # recursively call completion message to give the LLM a chance to process results
        return complete_with_llm(message_list)


def convert_markdown_to_slack_markup(text):
    text = re.sub(r'\*\*(.+?)\*\*', r'*\1*', text)  # bold
    text = re.sub(r'\*(.+?)\*', r'_\1_', text)  # italic
    text = re.sub(r'~~(.+?)~~', r'~\1~', text)  # strikethrough
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<\2|\1>', text)  # links
    text = re.sub(r'^(#+)\s*(.+)', lambda m: '*' + m.group(2) + '*', text, flags=re.MULTILINE)  # headers

    return text


if __name__ == '__main__':
    handler = SocketModeHandler(app, os.environ.get('SLACK_APP_TOKEN'))
    handler.start()
