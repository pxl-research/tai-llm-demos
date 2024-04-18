import os
import time

import tiktoken
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()

client = AzureOpenAI(
    api_key=os.getenv("AOA_API_KEY"),
    api_version="2024-02-15-preview",
    azure_endpoint=os.getenv("AOA_ENDPOINT"),
)

general_instructions = ("Be concise, but precise as well."
                        "Always think step by step."
                        "Take a deep breath before responding.")

assistant = client.beta.assistants.create(
    name="Professional Assistant",
    description="You support a team of applied researchers operating in Western Europe.",
    instructions=general_instructions,
    model="gpt-4-1106-preview",
    tools=[{"type": "code_interpreter"}],
)

thread = client.beta.threads.create()


def clear_log():
    global thread
    thread = client.beta.threads.create()
    return ["", ""]


def store_thread(a_thread, log_folder):
    messages = client.beta.threads.messages.list(
        thread_id=a_thread.id,
        order="asc"
    )
    log_string = messages.model_dump_json(indent=2)

    if not os.path.exists(log_folder):
        os.makedirs(log_folder)

    log_file = open(f"{log_folder}{a_thread.id}.json", "w")
    log_file.write(log_string)
    log_file.close()


def append_user(message, chat_history):
    chat_history.append((message, None))
    return chat_history


def append_ai(message, chat_history, log_folder):
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
        time.sleep(0.25)
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        time_diff = round((time.time() - start_time), 1)
        status = run.status
        print(f"Elapsed time: {time_diff} seconds, Status: {status}")

    messages = client.beta.threads.messages.list(
        thread_id=thread.id,
        order="desc",
        limit=1
    )

    bot_message = ""
    for msgData in messages.data:
        if msgData.role == "assistant" and msgData.content[0].type == "text":
            bot_message = msgData.content[0].text.value
            break
    chat_history.append((None, bot_message))

    # cost estimate
    (token_count, cost_in_cents) = estimate_costs(chat_history)
    debug = f"Cost estimate for {token_count} tokens: {cost_in_cents:.2f} cents"

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
    cost_prompts = round(token_count_prompts / 1000 * 1, 2)
    cost_responses = round(token_count_responses / 1000 * 3, 2)

    return (token_count_prompts + token_count_responses), (cost_prompts + cost_responses)
