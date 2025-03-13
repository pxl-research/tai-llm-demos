import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

if not os.getenv('OPENROUTER_ENDPOINT') or not os.getenv('OPENROUTER_API_KEY'):
    raise ValueError("Missing required environment variables. "
                     "Please ensure OPENROUTER_ENDPOINT and OPENROUTER_API_KEY are set in .env file.")


client = OpenAI(
    base_url=os.getenv('OPENROUTER_ENDPOINT'),
    api_key=os.getenv('OPENROUTER_API_KEY'),
)

system_instruction = {
    'role': 'system',
    'content': 'You are an assistant summarizing notes based off audio transcripts. '
               'Try to always summarize the essential parts of the audio fragment in a bulleted list. '
               'Use the same language as the source material (e.g. Dutch summary for Dutch transcripts). '
               'Use Markdown syntax to format your response more clearly. '
               'Be concise and precise. '
               'I would like you to take a deep breath before responding. '
}


def summarize_message(message):
    history = [system_instruction]
    history.append({'role': 'user', 'content': message})

    response_stream = client.chat.completions.create(model='google/gemini-2.0-flash-001',
                                                     messages=history,
                                                     extra_headers={
                                                         'HTTP-Referer': 'https://pxl-research.be/',
                                                         'X-Title': 'PXL Smart ICT'
                                                     },
                                                     stream=True)

    partial_message = ''
    for chunk in response_stream:  # stream the response
        if len(chunk.choices) > 0 and chunk.choices[0].delta.content is not None:
            partial_message = partial_message + chunk.choices[0].delta.content
            yield partial_message
