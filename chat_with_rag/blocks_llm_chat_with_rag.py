import json
import os
import sys
import time

import tiktoken
from dotenv import load_dotenv
from openai import AzureOpenAI

sys.path.append('../')

from demos.tool_calling.tool_descriptors import tools_rag_descriptor
# noinspection PyUnresolvedReferences
from fn_rag import lookup_in_documentation

load_dotenv()

client = AzureOpenAI(
    api_key=os.getenv("AOA_API_KEY"),
    api_version="2024-02-15-preview",
    azure_endpoint=os.getenv("AOA_ENDPOINT"),
)

general_instructions = ("Be concise, but precise as well. "
                        "Always think step by step. "
                        "Take a deep breath before responding. "
                        "Feel free to use Markdown syntax in your answer."
                        "When using an external source, always include the reference. ")

tools = [
    {"type": "code_interpreter"},
    tools_rag_descriptor
]

assistant = client.beta.assistants.create(
    name="Professional Assistant",
    description="You support a team of applied researchers operating in Western Europe.",
    instructions=general_instructions,
    model="gpt-4o-mini",
    tools=tools,
)


def clear_chat():
    thread = client.beta.threads.create()
    return ["", "", thread]


def store_thread(thread, log_folder):
    messages = client.beta.threads.messages.list(
        thread_id=thread.id,
        order="asc"
    )
    log_string = messages.model_dump_json(indent=2)

    if not os.path.exists(log_folder):
        os.makedirs(log_folder)

    log_file = open(f"{log_folder}{thread.id}.json", "w")
    log_file.write(log_string)
    log_file.close()


def append_user(message, chat_history):
    chat_history.append((message, None))
    return chat_history


def call_to_action(run, thread):
    function_calls = run.required_action.submit_tool_outputs.tool_calls
    function_results = {}
    for function_call in function_calls:
        function_name = function_call.function.name
        print(f"Function name: {function_name}")
        fn_pointer = globals()[function_name]

        if fn_pointer is not None:
            query = json.loads(function_call.function.arguments)["query"]
            result = fn_pointer(query)
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

    bot_message = ""
    for msg_data in messages.data:
        if msg_data.role == "assistant" and msg_data.content[0].type == "text":
            bot_message = msg_data.content[0].text.value
            break
    chat_history.append((None, bot_message))

    # cost estimate
    (token_count, cost_in_cents) = estimate_costs(chat_history)
    debug = f"Cost estimate for {token_count} tokens: {cost_in_cents:.3f} cents"

    store_thread(thread, log_folder)
    return "", chat_history, debug


def estimate_costs(chat_history):
    prompt_log = ""
    response_log = ""
    for user_msg, bot_msg in chat_history:
        if user_msg:
            prompt_log = prompt_log + user_msg
        if bot_msg:
            response_log = response_log + bot_msg

    tokeniser = tiktoken.encoding_for_model("gpt-4")
    token_count_prompts = len(tokeniser.encode(prompt_log))
    token_count_responses = len(tokeniser.encode(response_log))
    input_1k = 0.00015
    output_1k = 0.00060
    # WARNING: this is an underestimation because we do not take the RAG / context into account
    # TEMP WORKAROUND: we do this * 10
    # TODO: fix this calculation
    cost_prompts = round(token_count_prompts / 1000 * input_1k * 10, 4)
    cost_responses = round(token_count_responses / 1000 * output_1k * 10, 4)

    return (token_count_prompts + token_count_responses), (cost_prompts + cost_responses)
