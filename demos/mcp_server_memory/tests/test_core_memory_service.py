import os
import sys

from faker import Faker

# Get the absolute path to the project root
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from memory_service.core_memory_service import initialize_memory, store_memory, retrieve_memory


# Test environment setup
def test_initialization():
    print("Testing initialize_memory...")

    # Test case 1: Initialize without reset
    result = initialize_memory(reset=False)
    if result['status'] == 'success':
        print("initialize_memory without reset: PASSED")
    else:
        print("initialize_memory without reset: FAILED")

    # Test case 2: Initialize with reset
    result = initialize_memory(reset=True)
    if result['status'] == 'success':
        print("initialize_memory with reset: PASSED")
    else:
        print("initialize_memory with reset: FAILED")


def test_store_memory(memory_str: str):
    print("Testing store_memory...")

    content = memory_str
    wordlist = memory_str.split(' ')
    topic = wordlist[0]
    tags = [topic, wordlist[1], wordlist[2]]

    store_result = store_memory(content=content, topic=topic, tags=tags)

    if store_result['status'] == 'success':
        print("store_memory: PASSED")
        print(f"Stored Memory: {store_result}")
    else:
        print("store_memory: FAILED")
        print(f"Error: {store_result['message']}")
    return store_result


def test_retrieve_memory(store_result):
    print("Testing retrieve_memory...")

    memory_id = store_result['memory_id']
    topic = store_result['topic']
    print(f"Stored Memory ID: {memory_id}")

    # Retrieve the stored memory
    query = topic
    retrieve_result = retrieve_memory(query=query, max_results=1, topic=None, return_type="both")[0]
    if retrieve_result and 'id' in retrieve_result and retrieve_result['id'] == memory_id:
        print("retrieve_memory: PASSED")
        print(f"Retrieved Memory: {retrieve_result}")
        return

    # else
    print("retrieve_memory: FAILED")
    print(f"Error: {retrieve_result['message']}")


if __name__ == "__main__":
    test_initialization()
    print()

    faker_inst = Faker()
    memory = "Mind uploading is a speculative process of whole brain emulation in which a brain scan is used to completely emulate the mental state of the individual in a digital computer. The computer would then run a simulation of the brain's information processing, such that it would respond in essentially the same way as the original brain and experience having a sentient conscious mind."
    store_result = test_store_memory(memory_str=memory)
    print()

    if store_result['status'] == 'success':
        test_retrieve_memory(store_result)
