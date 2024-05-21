from abc import abstractmethod, ABC


class DocumentLoader(ABC):
    """
    Abstract base class for a document loader.
    """

    @abstractmethod
    def load_document(self, file_path: str) -> str:
        """
        Abstract method to convert a document to a string with markdown.
        """
        pass
