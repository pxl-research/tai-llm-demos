from abc import abstractmethod, ABC


class Splitter(ABC):
    """
    Abstract base class for a text splitter.
    """

    @abstractmethod
    def split(self, doc: str):
        """
        Abstract method to split a text document into chunks.
        """
        pass
