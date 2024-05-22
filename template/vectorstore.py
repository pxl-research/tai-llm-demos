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

    @abstractmethod
    def add_folder(self, file_path: str):
        """
        Abstract method to add a folder to the vector store.
        """
        pass

    @abstractmethod
    def delete_document(self, doc_title: str):
        """
        Abstract method to delete a document from the vector store.
        """
        pass
