from abc import ABC, abstractmethod


class EmbeddingsManager(ABC):
    """
    Abstract base class for an embedding manager.
    """

    @abstractmethod
    def get_embeddings(self):
        """
        Abstract method to get embeddings from a model.
        """
        pass
