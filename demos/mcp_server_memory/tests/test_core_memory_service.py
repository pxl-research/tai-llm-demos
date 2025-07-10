import os
import sys

# Get the absolute path to the project root
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from memory_service.core_memory_service import initialize_memory, store_memory, retrieve_memory, update_memory, delete_memory


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


def test_update_memory(store_result):
    print("Testing update_memory...")

    memory_id = store_result['memory_id']

    # Update the content of the memory
    new_content = "Substantial mainstream research in related areas is being conducted in neuroscience and computer science, including animal brain mapping and simulation,[4] development of faster supercomputers, virtual reality, brain–computer interfaces, connectomics, and information extraction from dynamically functioning brains.[5] According to supporters, many of the tools and ideas needed to achieve mind uploading already exist or are under active development; however, they will admit that others are, as yet, very speculative, but say they are still in the realm of engineering possibility."
    update_result = update_memory(memory_id=memory_id, content=new_content)
    if update_result['status'] == 'success':
        print("update_memory (content): PASSED")
        print(f"Updated Memory: {update_result}")
    else:
        print("update_memory (content): FAILED")
        print(f"Error: {update_result['message']}")

    # Update the topic and tags of the memory
    wordlist = new_content.split(' ')
    new_topic = wordlist[0]
    new_tags = [new_topic, wordlist[1], wordlist[2]]

    update_result = update_memory(memory_id=memory_id, topic=new_topic, tags=new_tags)
    if update_result['status'] == 'success':
        print("update_memory (topic and tags): PASSED")
        print(f"Updated Memory: {update_result}")
    else:
        print("update_memory (topic and tags): FAILED")
        print(f"Error: {update_result['message']}")

    # Attempt to update a non-existent memory
    invalid_memory_id = "non_existent_id"
    update_result = update_memory(memory_id=invalid_memory_id, content="Invalid update")
    if update_result['status'] == 'success':
        print("update_memory (non-existent): FAILED")
    else:
        print("update_memory (non-existent): PASSED")
        print(f"Error: {update_result['message']}")


def test_delete_memory(store_result):
    print("Testing delete_memory...")

    memory_id = store_result['memory_id']

    # Delete the stored memory
    delete_result = delete_memory(memory_id=memory_id)
    if delete_result['status'] == 'success':
        print("delete_memory: PASSED")
    else:
        print("delete_memory: FAILED")
        print(f"Error: {delete_result['message']}")

    # Attempt to delete a non-existent memory
    invalid_memory_id = "non_existent_id"
    delete_result = delete_memory(memory_id=invalid_memory_id)
    if delete_result['status'] == 'success':
        print("delete_memory (non-existent): FAILED")
    else:
        print("delete_memory (non-existent): PASSED")
        print(f"Error: {delete_result['message']}")


if __name__ == "__main__":
    test_initialization()
    print()

    # test storing and retrieving memories
    memory_1 = "Mind uploading is a speculative process of whole brain emulation in which a brain scan is used to completely emulate the mental state of the individual in a digital computer. The computer would then run a simulation of the brain's information processing, such that it would respond in essentially the same way as the original brain and experience having a sentient conscious mind."
    print(f"Generated Memory 1: {memory_1}")
    store_result_1 = test_store_memory(memory_str=memory_1)
    print()

    if store_result_1['status'] == 'success':
        test_retrieve_memory(store_result_1)
        print()

    memory_2 = "Spyridon Marinatos (Greek: Σπυρίδων Μαρινάτος; 17 November [O.S. 4 November] 1901[a] – 1 October 1974) was a Greek archaeologist who specialised in the Minoan and Mycenaean civilizations of the Aegean Bronze Age. He is best known for the excavation of the Minoan site of Akrotiri on Thera,[b] which he conducted between 1967 and 1974. He received several honours in Greece and abroad, and was considered one of the most important Greek archaeologists of his day."
    store_result_2 = test_store_memory(memory_str=memory_2)
    print()

    if store_result_2['status'] == 'success':
        test_retrieve_memory(store_result_2)
        print()

    # test updating the first memory
    if store_result_1['status'] == 'success':
        test_update_memory(store_result_1)
        print()

    # test deleting memory
    if store_result_2['status'] == 'success':
        test_delete_memory(store_result_2)
        print()
