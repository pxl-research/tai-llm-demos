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

                # Add progress container above upload widget
                self.upload_progress_container = ui.column().classes('w-full gap-2 mb-3')

                self.upload_widget = ui.upload(
                    on_upload=self._handle_file_upload,
                    auto_upload=True,
                    multiple=True
                ).props('accept=.pdf,.docx,.pptx,.xlsx,.xls max-file-size=26214400 aria-label="Upload documents for RAG. Supported: PDF, DOCX, PPTX, XLSX, XLS. Max 25 MB"')

            # Status
            self.status_label = ui.label('Ready').classes('text-sm text-gray-600')

            # Documents list
            ui.label('Indexed Documents').classes('font-semibold text-sm mt-3')

            self.documents_list = ui.column().classes('w-full gap-2')

            # Refresh button
            ui.button(
                'Refresh List',
                on_click=self._refresh_documents
            ).props('flat outline small aria-label="Refresh document list"').classes('w-full')

            # Initial load
            self._refresh_documents()

    def _handle_file_upload(self, e):
        """Handle file upload with step-by-step progress."""
        try:
            uploaded_file = e.file
            file_name = uploaded_file.name

            # Calculate file size
            if hasattr(uploaded_file, '_data'):
                file_size_bytes = len(uploaded_file._data)
            elif hasattr(uploaded_file, '_path'):
                file_size_bytes = Path(uploaded_file._path).stat().st_size
            else:
                file_size_bytes = 0

            file_size_mb = file_size_bytes / (1024 * 1024)

            # Check 25 MB limit
            if file_size_mb > 25:
                self.status_label.text = f'✗ File too large: {file_size_mb:.1f} MB (max 25 MB)'
                ui.notify(f'File exceeds 25 MB limit', type='negative')
                return

            # Create progress card
            with self.upload_progress_container:
                progress_card = ui.card().classes('w-full bg-blue-50 border-blue-200 p-3')
                with progress_card:
                    # Header: filename and size
                    with ui.row().classes('w-full items-center gap-2'):
                        ui.icon('description').classes('text-blue-600')
                        ui.label(file_name).classes('font-semibold flex-grow text-sm')
                        ui.label(f"{file_size_mb:.1f} MB").classes('text-xs text-gray-600')

                    # Progress steps
                    with ui.column().classes('w-full gap-1 mt-2'):
                        step1 = ui.label("⏳ Uploading...").classes('text-xs text-blue-600')
                        step2 = ui.label("⏺ Converting to markdown...").classes('text-xs text-gray-400')
                        step3 = ui.label("⏺ Indexing content...").classes('text-xs text-gray-400')

            # Get file path
            if hasattr(uploaded_file, '_path'):
                temp_path = uploaded_file._path
            elif hasattr(uploaded_file, '_data'):
                temp_path = Path('/tmp') / file_name
                with open(temp_path, 'wb') as f:
                    f.write(uploaded_file._data)
            else:
                raise ValueError(f"Unknown upload type: {type(uploaded_file)}")

            # Step 1: Upload complete
            step1.set_text("✓ Uploaded")
            step1.classes(remove='text-blue-600', add='text-green-600')

            # Step 2: Converting
            step2.set_text("⏳ Converting to markdown...")
            step2.classes(remove='text-gray-400', add='text-blue-600')

            # Step 3: Indexing (conversion happens inside add_document)
            step2.set_text("✓ Converted")
            step2.classes(remove='text-blue-600', add='text-green-600')
            step3.set_text("⏳ Indexing content...")
            step3.classes(remove='text-gray-400', add='text-blue-600')

            # Process document
            success = self.rag_service.add_document(str(temp_path))

            if success:
                # Success
                step3.set_text("✓ Indexed")
                step3.classes(remove='text-blue-600', add='text-green-600')
                self.status_label.text = f'✓ Added {file_name}'
                self.on_document_added(file_name)
                self._refresh_documents()
                ui.notify(f'Added {file_name}', type='positive')

                # Auto-remove progress card after 3 seconds
                ui.timer(3.0, lambda: progress_card.delete(), once=True)
            else:
                # Failed
                step3.set_text("✗ Failed to index")
                step3.classes(remove='text-blue-600', add='text-red-600')
                progress_card.classes(remove='bg-blue-50 border-blue-200', add='bg-red-50 border-red-200')
                self.status_label.text = f'✗ Failed to add {file_name}'
                ui.notify(f'Failed to add {file_name}', type='negative')

            # Cleanup temp file
            if hasattr(uploaded_file, '_data'):
                Path(temp_path).unlink(missing_ok=True)

        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"ERROR in upload: {error_trace}")
            self.status_label.text = f'Error: {str(e)[:50]}'
            ui.notify(f'Upload error: {str(e)[:50]}', type='negative')

            # Show error in progress card if exists
            if 'progress_card' in locals():
                progress_card.classes(remove='bg-blue-50', add='bg-red-50')
                with progress_card:
                    ui.label(f"❌ {str(e)[:100]}").classes('text-xs text-red-600 mt-2')

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
                        ).props(f'flat small dense aria-label="Delete document {doc_name}"')

    def get_documents(self) -> list:
        """Get list of indexed documents."""
        return self.rag_service.list_documents()

    def _delete_document(self, doc_name: str):
        """Delete document with confirmation dialog."""
        with ui.dialog() as confirm_dialog, ui.card():
            ui.label(f'Delete "{doc_name}"?').classes('text-lg font-semibold')
            ui.label('This will permanently remove the document from your knowledge base.').classes('text-sm text-gray-600 mt-2')

            with ui.row().classes('w-full justify-end gap-2 mt-4'):
                ui.button('Cancel', on_click=confirm_dialog.close).props('flat')
                ui.button(
                    'Delete',
                    on_click=lambda: self._perform_delete(doc_name, confirm_dialog)
                ).props('color=negative')

        confirm_dialog.open()

    def _perform_delete(self, doc_name: str, dialog):
        """Execute the deletion."""
        try:
            success = self.rag_service.remove_document(doc_name)
            if success:
                self.status_label.text = f'✓ Deleted {doc_name}'
                self.on_document_removed(doc_name)
                self._refresh_documents()
                dialog.close()
                ui.notify(f'Deleted {doc_name}', type='positive')
            else:
                self.status_label.text = f'Failed to delete {doc_name}'
                ui.notify(f'Failed to delete {doc_name}', type='negative')
        except Exception as e:
            self.status_label.text = f'Error: {str(e)[:50]}'
            ui.notify(f'Delete error: {str(e)}', type='negative')
