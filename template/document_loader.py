from abc import abstractmethod, ABC


class DocumentLoader(ABC):
    """
    Abstract base class for a document loader.
    """

    @abstractmethod
    def convert_to_markdown(self, file_path: str) -> str:
        """
        Abstract method to convert a document to a string with markdown.
        """
        pass
