from abc import abstractmethod, ABC


class TextSplitter(ABC):
    """
    Abstract base class for a text splitter.
    """

    @abstractmethod
    def split(self, markdown_text: str, meta_info=None, index_offset: int = 0) -> list:
        """
        Abstract method to split a text document into chunks.
        """
        pass
