import os
import sys
import uuid
import json
import shutil

# Get the absolute path to the project root
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from db.chroma_manager import ChromaManager
from config import CHROMA_PATH, MEMORY_COLLECTION, TOPICS_COLLECTION, SUMMARY_COLLECTION

# Initialize ChromaManager
shutil.rmtree(CHROMA_PATH, ignore_errors=True)
chroma_man = ChromaManager()


def main():
    # Reset the database for testing
    chroma_man.initialize(reset=False)

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


def test_update_topic():
    print("Testing update_topic...")
    topic = "updated_topic"
    tags = ["test", "topic"]

    if chroma_man.update_topic(topic, tags):
        print("update_topic: PASSED")
    else:
        print("update_topic: FAILED")
        return

    # Verify that the topic was updated correctly
    retrieved_topic = chroma_man.get_topic(topic)
    print(retrieved_topic)
    if retrieved_topic and json.loads(retrieved_topic["tags"]) == tags:
        print("update_topic verification: PASSED")
    else:
        print("update_topic verification: FAILED")
    print()


def test_get_status():
    print("Testing get_status...")
    status = chroma_man.get_status()
    if isinstance(status, dict):
        print("get_status: PASSED")
    else:
        print("get_status: FAILED")
    print()


def test_store_summary_embedding():
    print("Testing store_summary_embedding...")
    summary_id = str(uuid.uuid4())
    summary_text = "This is a test summary."
    metadata = {"test": "metadata"}

    if chroma_man.store_summary_embedding(summary_id, summary_text, metadata):
        print("store_summary_embedding: PASSED")
    else:
        print("store_summary_embedding: FAILED")
        return

    # Verify that the summary was stored correctly
    retrieved_summary = chroma_man.get_summary_by_id(summary_id)
    if retrieved_summary and retrieved_summary["summary_text"] == summary_text and retrieved_summary["test"] == "metadata":
        print("store_summary_embedding verification: PASSED")
    else:
        print("store_summary_embedding verification: FAILED")
    print()


def test_summary_embeddings():
    print("Testing search_summary_embeddings and delete_summary_embeddings...")
    summary_id = str(uuid.uuid4())
    summary_text = "This is a test summary for embeddings."
    metadata = {"test": "embeddings"}

    if not chroma_man.store_summary_embedding(summary_id, summary_text, metadata):
        print("store_summary_embedding: FAILED")
        return

    # Search for the summary embedding
    results = chroma_man.search_summary_embeddings(summary_text)
    if results and summary_id in results:
        print("search_summary_embeddings: PASSED")
    else:
        print("search_summary_embeddings: FAILED")
        return

    # Delete the summary embedding
    if not chroma_man.delete_summary_embeddings(summary_id):
        print("delete_summary_embeddings: FAILED")
        return

    # Search for the summary embedding again to verify deletion
    results = chroma_man.search_summary_embeddings(summary_text)
    if not results or summary_id not in results:
        print("delete_summary_embeddings verification: PASSED")
    else:
        print("delete_summary_embeddings verification: FAILED")
    print()


def test_delete_memory():
    print("Testing delete_memory...")
    memory_id = str(uuid.uuid4())
    content = "This is a test memory for deletion."
    topic = "test_topic"
    tags = ["test", "deletion"]

    if not chroma_man.store_memory(memory_id, content, topic, tags):
        print("store_memory: FAILED")
        return

    if not chroma_man.delete_memory(memory_id):
        print("delete_memory: FAILED")
        return

    # Verify that the memory was deleted
    results = chroma_man.search_memories(content, topic=topic)
    if not results or memory_id not in results:
        print("delete_memory verification: PASSED")
    else:
        print("delete_memory verification: FAILED")
    print()


if __name__ == "__main__":
    main()
    test_store_memory()
    test_update_memory()
    test_update_topic()
    test_get_status()
    test_store_summary_embedding()
    test_summary_embeddings()
    test_delete_memory()
