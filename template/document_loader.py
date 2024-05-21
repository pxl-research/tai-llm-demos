from abc import abstractmethod, ABC


class DocumentLoader(ABC):
    """
    Abstract base class for a retriever.
    """

    @abstractmethod
    def load_document(self, file_path: str):
        """
        Abstract method to retrieve chunks from a vector store.
        """
        pass
