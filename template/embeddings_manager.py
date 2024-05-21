from abc import ABC, abstractmethod


class EmbeddingsManager(ABC):
    """
    Abstract base class for an embeddings manager.
    """

    def __init__(self):
        self.embeddings = None

    @abstractmethod
    def get_embeddings(self):
        """
        Abstract method to get embeddings from a model.
        """
        pass
