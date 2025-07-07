import json
import os
import sys
import time

import tiktoken
from dotenv import load_dotenv
from openai import AzureOpenAI

sys.path.append('../../')

from demos.tool_calling.tool_descriptors import tools_rag_descriptor
# noinspection PyUnresolvedReferences
from fn_rag import lookup_in_documentation, list_documents

load_dotenv()

client = AzureOpenAI(
    api_key=os.getenv("AOA_API_KEY"),
    api_version="2024-02-15-preview",
    azure_endpoint=os.getenv("AOA_ENDPOINT"),
)

general_instructions = ("I would like you to take a deep breath before responding. "
                        "Always think step by step. "
                        "Be concise and precise in your responses. "
                        "Answer using Markdown syntax when appropriate. "
                        "If you do not know the answer to a question, just say you do not know. "
                        "Consult the documentation when appropriate. "
                        "When using an external source, always include the reference. ")

tools = tools_rag_descriptor
tools.append({"type": "code_interpreter"})

assistant = client.beta.assistants.create(
    name="Professional Assistant",
    description="You support a team of applied researchers operating in Western Europe.",
    instructions=general_instructions,
    model="gpt-4o-mini",
    tools=tools,
)


def clear_chat():
    """Reset the chat by creating a new thread and clearing chat state."""
    thread = client.beta.threads.create()
    return ["", "", thread]


def store_thread(thread, log_folder):
    """Persist the thread's messages to a log file in the specified folder."""
    messages = client.beta.threads.messages.list(
        thread_id=thread.id,
        order="asc"
    )
    log_string = messages.model_dump_json(indent=2)

    if not os.path.exists(log_folder):
        os.makedirs(log_folder)

    log_path = os.path.join(log_folder, f"{thread.id}.json")
    try:
        with open(log_path, "w") as log_file:
            log_file.write(log_string)
    except OSError as e:
        print(e)
        pass


def append_user(message, chat_history):
    """Append a user message to the chat history."""
    user_message = {"role": "user", "content": message}
    chat_history.append(user_message)
    return chat_history


def call_to_action(run, thread):
    function_calls = run.required_action.submit_tool_outputs.tool_calls
    function_results = {}
    for function_call in function_calls:
        function_name = function_call.function.name
        print(f"Function name: {function_name}")
        fn_pointer = globals()[function_name]

        if fn_pointer is not None:
            arguments = json.loads(function_call.function.arguments)
            if 'query' in arguments:
                query = arguments["query"]
                result = fn_pointer(query)
            else:
                result = fn_pointer()
            function_results[function_call.id] = result
        else:
            print(f"Unknown function name: {function_name}")

    # submit function responses
    outputs = []
    for function_call in function_calls:
        if function_call.id in function_results:
            outputs.append({
                "tool_call_id": function_call.id,
                "output": json.dumps(function_results[function_call.id]),
            })
        else:
            print(f"Function result not found: {function_call.id}")

    client.beta.threads.runs.submit_tool_outputs(
        thread_id=thread.id,
        run_id=run.id,
        tool_outputs=outputs,
    )


def append_ai(thread, message, chat_history, log_folder):
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
        time.sleep(0.33)
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        time_diff = round((time.time() - start_time), 1)
        status = run.status
        print(f"Elapsed time: {time_diff} seconds, Status: {status}")
        if run.status == "requires_action":
            call_to_action(run, thread)

    messages = client.beta.threads.messages.list(
        thread_id=thread.id,
        order="desc",
        limit=1
    )

    for msg_data in messages.data:
        if (msg_data.role == "assistant"
                and msg_data.content
                and len(msg_data.content) > 0
                and msg_data.content[0].type == "text"):
            bot_message = msg_data.content[0].text.value
            chat_history.append({"role": msg_data.role, "content": bot_message})

    # cost estimate
    (token_count_prompts, token_count_responses) = estimate_token_count(chat_history)
    debug = f"Token estimate:  {token_count_prompts} input tokens and {token_count_responses} output tokens."

    store_thread(thread, log_folder)
    return "", chat_history, debug


def estimate_token_count(chat_history):
    prompt_log = ""
    response_log = ""
    for msg in chat_history:
        if msg.get("role") == "user":
            prompt_log += msg["content"]
        elif msg.get("role") == "assistant":
            response_log += msg["content"]

    tokeniser = tiktoken.encoding_for_model("gpt-4")
    token_count_prompts = len(tokeniser.encode(prompt_log))
    token_count_responses = len(tokeniser.encode(response_log))

    return token_count_prompts, token_count_responses
