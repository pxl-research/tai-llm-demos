import os
import sys

# Get the absolute path to the project root
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from db.sqlite_manager import SQLiteManager
from config import SQLITE_PATH
import uuid


def main():
    # Initialize SQLiteManager
    db_manager = SQLiteManager()

    # Reset the database for testing
    db_manager.initialize(reset=True)

    # Test initialize
    print("Testing initialize...")
    if db_manager.initialize():
        print("initialize: PASSED")
    else:
        print("initialize: FAILED")
    print()

    memory_id = str(uuid.uuid4())
    print("Memory ID: {}".format(memory_id))

    # Test store_memory
    print("Testing store_memory...")
    content = "This is a test memory."
    topic = "test_topic"
    tags = ["test", "memory"]

    if db_manager.store_memory(memory_id, content, topic, tags):
        print("store_memory: PASSED")
    else:
        print("store_memory: FAILED")
    print()

    # Test get_memory
    print("Testing get_memory...")
    memory = db_manager.get_memory(memory_id)
    print(memory)
    if memory and memory["content"] == content and memory["topic_name"] == topic and memory["tags"] == tags:
        print("get_memory: PASSED")
    else:
        print("get_memory: FAILED")
    print()

    # Test update_memory
    print("Testing update_memory...")
    new_content = "This is an updated test memory."
    new_topic = "updated_topic"
    new_tags = ["updated", "memory"]

    if db_manager.update_memory(memory_id, content=new_content, topic=new_topic, tags=new_tags):
        print("update_memory: PASSED")
    else:
        print("update_memory: FAILED")

    updated_memory = db_manager.get_memory(memory_id)
    if updated_memory and updated_memory["content"] == new_content and updated_memory["topic_name"] == new_topic and \
            updated_memory["tags"] == new_tags:
        print("update_memory content check: PASSED")
    else:
        print("update_memory content check: FAILED")
    print()

    # Test list_topics
    print("Testing list_topics...")
    topics = db_manager.list_topics()
    print(topics)
    if topics and any(topic["name"] == new_topic for topic in topics):
        print("list_topics: PASSED")
    else:
        print("list_topics: FAILED")
    print()

    # Test get_status
    print("Testing get_status...")
    status = db_manager.get_status()
    print("Status: {}".format(status))
    if status and status["total_memories"] == 1 and status["total_topics"] >= 1:
        print("get_status: PASSED")
    else:
        print("get_status: FAILED")
    print()

    # Test store_summary
    print("Testing store_summary...")
    summary_id = str(uuid.uuid4())
    summary_type = "test_summary"
    summary_text = "This is a test summary."
    if db_manager.store_summary(summary_id, memory_id, summary_type, summary_text):
        print("store_summary: PASSED")
    else:
        print("store_summary: FAILED")
    print()

    # Test list_summary_types_by_memory_id
    print("Testing list_summary_types_by_memory_id...")
    summary_types = db_manager.list_summary_types_by_memory_id(memory_id)
    print(summary_types)
    if summary_types and any(s["summary_type"] == summary_type for s in summary_types):
        print("list_summary_types_by_memory_id: PASSED")
    else:
        print("list_summary_types_by_memory_id: FAILED")
    print()

    # Test get_summary
    print("Testing get_summary...")
    summary = db_manager.get_summary(memory_id, summary_type)
    print(summary)
    if summary and summary["summary_text"] == summary_text:
        print("get_summary: PASSED")
    else:
        print("get_summary: FAILED")
    print()

    # Test get_summary_by_id
    print("Testing get_summary_by_id...")
    summary_by_id = db_manager.get_summary_by_id(summary_id)
    if summary_by_id and summary_by_id["summary_text"] == summary_text:
        print("get_summary_by_id: PASSED")
    else:
        print("get_summary_by_id: FAILED")
    print()

    # Test update_summary
    print("Testing update_summary...")
    new_summary_text = "This is an updated test summary."
    if db_manager.update_summary(summary_id, new_summary_text):
        print("update_summary: PASSED")
    else:
        print("update_summary: FAILED")

    updated_summary = db_manager.get_summary_by_id(summary_id)
    print(updated_summary)
    if updated_summary and updated_summary["summary_text"] == new_summary_text:
        print("update_summary content check: PASSED")
    else:
        print("update_summary content check: FAILED")
    print()

    # Test delete_summaries
    print("Testing delete_summaries...")
    if db_manager.delete_summaries(memory_id):
        print("delete_summaries: PASSED")
    else:
        print("delete_summaries: FAILED")

    if db_manager.get_summary(memory_id, summary_type) is None:
        print("delete_summaries check: PASSED")
    else:
        print("delete_summaries check: FAILED")
    print()

    # Test delete_memory
    print("Testing delete_memory...")
    if db_manager.delete_memory(memory_id):
        print("delete_memory: PASSED")
    else:
        print("delete_memory: FAILED")
    if db_manager.get_memory(memory_id) is None:
        print("delete_memory check: PASSED")
    else:
        print("delete_memory check: FAILED")
    print()

    print("Checking if topics are empty...")
    topics = db_manager.list_topics()
    print(topics)
    if not any(topic["name"] == new_topic for topic in topics):
        print("delete_topic_if_empty check: PASSED")
    else:
        print("delete_topic_if_empty check: FAILED")
    print()

    # Test get_status
    print("Testing get_status...")
    status = db_manager.get_status()
    print("Status: {}".format(status))
    if status and status["total_memories"] == 0 and status["total_topics"] >= 0:
        print("get_status: PASSED")
    else:
        print("get_status: FAILED")
    print()


if __name__ == "__main__":
    main()
