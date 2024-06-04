import os
from abc import abstractmethod, ABC


class VectorStore(ABC):
    """
    Abstract base class for a vector store.
    """

    @abstractmethod
    def add_document(self, file_path: str):
        """
        Abstract method to add a document to the vector store.
        """
        pass

    def add_folder(self, folder_path: str):
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                self.add_document(os.path.join(root, file))

    @abstractmethod
    def delete_document(self, doc_title: str):
        """
        Abstract method to delete a document from the vector store.
        """
        pass
