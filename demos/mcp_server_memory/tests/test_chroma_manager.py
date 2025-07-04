import os
import sys
import uuid

# Get the absolute path to the project root
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from db.chroma_manager import ChromaManager
from config import CHROMA_PATH, MEMORY_COLLECTION, TOPICS_COLLECTION, SUMMARY_COLLECTION

# Initialize ChromaManager
chroma_man = ChromaManager()


def main():
    # Reset the database for testing
    chroma_man.initialize(reset=True)

    # Test initialize
    print("Testing initialize...")
    if chroma_man.initialize():
        print("initialize: PASSED")
    else:
        print("initialize: FAILED")
    print()


def test_store_memory():
    print("Testing store_memory...")
    memory_id = str(uuid.uuid4())
    content = "This is a test memory."
    topic = "test_topic"
    tags = ["test", "memory"]

    if chroma_man.store_memory(memory_id, content, topic, tags):
        print("store_memory: PASSED")
    else:
        print("store_memory: FAILED")
        return  # Skip further checks if store_memory failed

    # Verify that the memory was stored correctly
    results = chroma_man.search_memories(content, topic=topic)
    if memory_id in results:
        print("store_memory verification: PASSED")
    else:
        print("store_memory verification: FAILED")
    print()


def test_update_memory():
    print("Testing update_memory...")
    memory_id = str(uuid.uuid4())
    content = "This is a test memory."
    topic = "test_topic"
    tags = ["test", "memory"]

    if not chroma_man.store_memory(memory_id, content, topic, tags):
        print("store_memory: FAILED")
        return

    new_content = "This is an updated test memory."
    new_topic = "updated_topic"
    new_tags = ["updated", "memory"]

    if chroma_man.update_memory(memory_id, new_content, new_topic, new_tags):
        print("update_memory: PASSED")
    else:
        print("update_memory: FAILED")
        return

    # Verify that the memory was updated correctly
    results = chroma_man.search_memories(new_content, topic=new_topic)
    if memory_id in results:
        print("update_memory verification: PASSED")
    else:
        print("update_memory verification: FAILED")
    print()


if __name__ == "__main__":
    main()
    test_store_memory()
    test_update_memory()
