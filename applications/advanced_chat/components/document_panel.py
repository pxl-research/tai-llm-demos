"""
Document Panel Component: File upload and document management.
"""
import sys
from pathlib import Path
from typing import Callable

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from nicegui import ui
from services.rag_service import RAGService


class DocumentPanel:
    """Manages document upload and RAG document display."""

    def __init__(self, rag_service: RAGService, on_document_added: Callable, on_document_removed: Callable):
        """
        Initialize document panel.

        Args:
            rag_service: Shared RAG service instance
            on_document_added: Callback when document is added
            on_document_removed: Callback when document is removed
        """
        self.rag_service = rag_service
        self.on_document_added = on_document_added
        self.on_document_removed = on_document_removed
        self.documents_list = None
        self.upload_widget = None
        self.status_label = None

    def build_ui(self):
        """Build document panel UI."""
        with ui.column().classes('w-full gap-3'):
            ui.label('Documents').classes('text-h6 font-bold')

            # Upload area
            with ui.card().classes('w-full'):
                ui.label('Upload Documents').classes('font-semibold text-sm')
                ui.label(
                    'Supported: PDF, DOCX, PPTX, XLSX, XLS'
                ).classes('text-xs text-gray-600')

                self.upload_widget = ui.upload(
                    on_upload=self._on_upload,
                    auto_upload=True,
                    multiple=True
                ).props('accept=.pdf,.docx,.pptx,.xlsx,.xls')

            # Status
            self.status_label = ui.label('Ready').classes('text-sm text-gray-600')

            # Documents list
            ui.label('Indexed Documents').classes('font-semibold text-sm mt-3')

            self.documents_list = ui.column().classes('w-full gap-2')

            # Refresh button
            ui.button(
                'Refresh List',
                on_click=self._refresh_documents
            ).props('flat outline small').classes('w-full')

            # Initial load
            self._refresh_documents()

    def _on_upload(self, e):
        """Handle file upload."""
        try:
            # Access file from UploadEventArguments (NiceGUI 3.0.3)
            uploaded_file = e.file
            file_name = uploaded_file.name

            # Handle both LargeFileUpload (on disk) and SmallFileUpload (in memory)
            if hasattr(uploaded_file, '_path'):
                # LargeFileUpload - file already on disk
                temp_path = uploaded_file._path
            elif hasattr(uploaded_file, '_data'):
                # SmallFileUpload - file in memory
                temp_path = Path('/tmp') / file_name
                with open(temp_path, 'wb') as f:
                    f.write(uploaded_file._data)
            else:
                raise ValueError(f"Unknown upload type: {type(uploaded_file)}")

            # Process document (convert, chunk, add to ChromaDB)
            self.status_label.text = f'Processing {file_name}...'
            success = self.rag_service.add_document(str(temp_path))

            if success:
                self.status_label.text = f'✓ Added {file_name}'
                self.on_document_added(file_name)
                self._refresh_documents()
            else:
                self.status_label.text = f'✗ Failed to add {file_name}'

            # Clean up temp file only for SmallFileUpload
            if hasattr(uploaded_file, '_data'):
                Path(temp_path).unlink(missing_ok=True)

        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"ERROR in upload: {error_trace}")
            self.status_label.text = f'Error: {str(e)[:50]}'

    def _refresh_documents(self):
        """Refresh the documents list."""
        self.documents_list.clear()

        documents = self.rag_service.list_documents()

        if not documents:
            ui.label('No documents uploaded yet').classes('text-gray-500 italic')
        else:
            for doc_name in documents:
                with ui.card().classes('w-full'):
                    with ui.row().classes('w-full justify-between items-center'):
                        ui.label(doc_name).classes('flex-grow')
                        ui.button(
                            icon='delete',
                            on_click=lambda d=doc_name: self._delete_document(d)
                        ).props('flat small dense')

    def get_documents(self) -> list:
        """Get list of indexed documents."""
        return self.rag_service.list_documents()

    def _delete_document(self, doc_name: str):
        """Delete a document from RAG store."""
        try:
            success = self.rag_service.remove_document(doc_name)
            if success:
                self.status_label.text = f'Deleted {doc_name}'
                self.on_document_removed(doc_name)
                self._refresh_documents()
            else:
                self.status_label.text = f'Failed to delete {doc_name}'
        except Exception as e:
            self.status_label.text = f'Error: {str(e)[:50]}'
