from abc import abstractmethod, ABC

from template.document_loader import DocumentLoader
from template.embeddings_manager import EmbeddingsManager
from template.splitter import Splitter


class VectorStore(ABC):
    """
    Abstract base class for a vector store.
    """

    def __init__(self, collection_name: str,
                 doc_list_path: str,
                 document_loader: DocumentLoader,
                 splitter: Splitter,
                 embeddings_manager: EmbeddingsManager):
        self.collection_name = collection_name
        self.doc_list_path = doc_list_path
        self.doc_list = []  # read_csv(doc_list_path)
        self.document_loader = document_loader
        self.splitter = splitter
        self.embeddings_manager = embeddings_manager

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
