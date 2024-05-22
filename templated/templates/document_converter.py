from abc import abstractmethod, ABC


class DocumentConverter(ABC):
    """
    Abstract base class for a document converter.
    """

    @abstractmethod
    def convert_to_markdown_fulltext(self, file_path: str) -> str:
        """
        Abstract method to convert a document to a string with markdown.
        """
        pass

    @abstractmethod
    def convert_to_markdown_pages(self, file_path: str) -> list[str]:
        """
        Abstract method to convert a document to a list of pages with markdown.
        """
        pass
