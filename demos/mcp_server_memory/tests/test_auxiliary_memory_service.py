import os
import sys

# Get the absolute path to the project root
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from memory_service.auxiliary_memory_service import list_topics, get_status, summarize_memory
from memory_service.core_memory_service import initialize_memory, store_memory

memory_1 = "Mind uploading is a speculative process of whole brain emulation in which a brain scan is used to completely emulate the mental state of the individual in a digital computer. The computer would then run a simulation of the brain's information processing, such that it would respond in essentially the same way as the original brain and experience having a sentient conscious mind."
memory_2 = "Spyridon Marinatos (Greek: Σπυρίδων Μαρινάτος; 17 November [O.S. 4 November] 1901[a] – 1 October 1974) was a Greek archaeologist who specialised in the Minoan and Mycenaean civilizations of the Aegean Bronze Age. He is best known for the excavation of the Minoan site of Akrotiri on Thera,[b] which he conducted between 1967 and 1974. He received several honours in Greece and abroad, and was considered one of the most important Greek archaeologists of his day."


# Test environment setup
def test_list_topics():
    print("Testing list_topics...")

    # Ensure a clean state for the test
    initialize_memory(reset=True)

    # Test case: List topics when no topics exist
    result = list_topics()
    if (result and isinstance(result, list) and len(result) == 1
            and 'message' in result[0] and result[0]['message'] == "No topics found"):
        print("list_topics (no topics): PASSED")
        print(f"Result: {result}")
    else:
        print("list_topics (no topics): FAILED")
        print(f"Error: {result}")

    # add some memories

    store_a_memory(memory_str=memory_1)
    store_a_memory(memory_str=memory_2)

    result = list_topics()
    # Fix misleading print statement in the second list_topics test case
    if result and isinstance(result, list) and len(result) > 1:
        print("list_topics (with topics): PASSED")
        print(f"Result: {result}")
    else:
        print("list_topics (with topics): FAILED")
        print(f"Error: {result}")


def test_get_status():
    print("Testing get_status...")

    # Ensure a clean state for the test
    initialize_memory(reset=True)

    # Test case: Get status when memory system is empty
    result = get_status()
    if (result['status'] == 'success' and 'stats' in result and
            result['stats']['total_memories'] == 0 and
            result['stats']['total_topics'] == 0 and
            isinstance(result['stats']['top_topics'], list) and len(result['stats']['top_topics']) == 0):
        print("get_status (empty): PASSED")
        print(f"Result: {result}")
    else:
        print("get_status (empty): FAILED")
        print(f"Error: {result}")

    # Add some memories
    memory_1 = "This is a test memory for status check."
    store_a_memory(memory_str=memory_1)
    memory_2 = "Another test memory to verify status updates."
    store_a_memory(memory_str=memory_2)

    # Test case: Get status after adding memories
    result = get_status()
    if (result['status'] == 'success' and 'stats' in result and
            result['stats']['total_memories'] >= 2 and
            result['stats']['total_topics'] > 0 and
            isinstance(result['stats']['top_topics'], list) and len(result['stats']['top_topics']) > 0):
        print("get_status (with data): PASSED")
        print(f"Result: {result}")
    else:
        print("get_status (with data): FAILED")
        print(f"Error: {result}")


def test_summarize_memory():
    print("Testing summarize_memory...")

    # Ensure a clean state for the test
    initialize_memory(reset=True)

    # Add a memory to summarize
    store_result = store_a_memory(memory_str=memory_1)
    if store_result['status'] != 'success':
        print("store_a_memory for summarize_memory test: FAILED")
        print(f"Error: {store_result['message']}")
        return

    memory_id = store_result['memory_id']

    # Test case: Summarize by memory_id
    result = summarize_memory(memory_id=memory_id, summary_type="abstractive", length="medium")
    print(result)
    if result['status'] == 'success' and 'summary' in result:
        print("summarize_memory (by memory_id): PASSED")
        print(f"Summary: {result['summary']}")
    else:
        print("summarize_memory (by memory_id): FAILED")
        print(f"Error: {result['message']}")

    # Test case: Summarize by query
    query = "test memory"
    result = summarize_memory(query=query, summary_type="query_focused", length="short")
    if result['status'] == 'success' and 'summary' in result:
        print("summarize_memory (by query): PASSED")
        print(f"Summary: {result['summary']}")
    else:
        print("summarize_memory (by query): FAILED")
        print(f"Error: {result['message']}")

    # Test case: Summarize by topic
    topic = memory_1.split(' ')[0]
    result = summarize_memory(topic=topic, summary_type="extractive", length="detailed")
    if result['status'] == 'success' and 'summary' in result:
        print("summarize_memory (by topic): PASSED")
        print(f"Summary: {result['summary']}")
    else:
        print("summarize_memory (by topic): FAILED")
        print(f"Error: {result['message']}")


def store_a_memory(memory_str: str):
    content = memory_str
    wordlist = memory_str.split(' ')
    topic = wordlist[0]
    tags = [topic, wordlist[1], wordlist[2]]

    store_result = store_memory(content=content, topic=topic, tags=tags)
    return store_result


if __name__ == "__main__":
    # Run the test for getting status
    test_get_status()
    print()

    # Run the test for listing topics
    test_list_topics()
    print()

    # Run the test for summarizing memory
    test_summarize_memory()
