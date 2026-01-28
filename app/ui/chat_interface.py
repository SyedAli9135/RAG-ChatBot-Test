import httpx

from nicegui import ui

from app.config import settings

# backend URL
BACKEND_URL = settings.backend_url


class ChatInterface:
    """Chat interface.
    Streaming responses displays, PDF uploads manages, status shows.
    """

    def __init__(self):
        """Initialize interface, UI components"""
        self.messages = []
        self.session_id = "nicegui_session_001"
        self.chat_container = None
        self.input_field = None
        self.status_label = None
        self.send_button = None
        self.upload_status = None

    def create_ui(self):
        """
        Create UI layout
        """
        ui.colors(primary='#1976D2')

        with ui.column().classes('w-full h-screen p-4'):
            # Header
            with ui.row().classes('w-full items-center mb-4'):
                ui.label('RAG Chatbot').classes('text-2xl font-bold')
                ui.space()
                self.status_label = ui.label(
                    'Ready').classes('text-sm text-gray-500')

            # PDF Upload Section
            with ui.card().classes('w-full mb-4'):
                ui.label('Upload PDF Document').classes(
                    'text-lg font-semibold mb-2')

                with ui.row().classes('items-center gap-2'):
                    # File upload, PDF only accept we do
                    upload = ui.upload(
                        label='Choose PDF',
                        auto_upload=True,
                        on_upload=self.handle_upload,
                    ).props('accept=".pdf"')

                    self.upload_status = ui.label('').classes('text-sm')

            # Chat Container
            with ui.card().classes('w-full flex-grow'):
                ui.label('Chat').classes('text-lg font-semibold mb-2')

                # Scrollable chat area
                self.chat_container = ui.column().classes(
                    'w-full h-96 overflow-y-auto p-2 bg-gray-50 rounded').props(f'id=chat_container')
                self.chat_container.props(f'id={self.chat_container.id}')

                # Input area
                with ui.row().classes('w-full gap-2 mt-4'):
                    self.input_field = ui.input(
                        label='Type your message...',
                        placeholder='Ask about the uploaded document...',
                    ).classes('flex-grow').on('keydown.enter', self.send_message)

                    self.send_button = ui.button(
                        'Send',
                        on_click=self.send_message,
                    ).props('icon=send')

            # Info footer
            ui.label('Upload a PDF, then ask questions about it!').classes(
                'text-sm text-gray-500 mt-2')

    async def handle_upload(self, event):
        """
        Handle PDF upload, async operation.
        """
        try:
            # Update status - Received
            self.set_status('Uploading PDF...', 'uploading')
            self.upload_status.set_text('Uploading...')

            file_obj = event.file
            filename = file_obj.name
            content = await file_obj.read()

            # Validate PDF extension
            if not filename.lower().endswith('.pdf'):
                self.upload_status.set_text('Only PDF files allowed!')
                self.set_status('Ready', 'ready')
                return

            # Upload to backend
            async with httpx.AsyncClient(timeout=120.0) as client:
                files = {'file': (filename, content,
                                  'application/pdf')}

                # Update status - Processing
                self.set_status('Processing PDF...', 'processing')
                self.upload_status.set_text('Processing...')

                response = await client.post(
                    f'{BACKEND_URL}/api/upload/pdf',
                    files=files,
                )

                if response.status_code == 200:
                    data = response.json()
                    # Success!
                    self.upload_status.set_text(f'{filename} uploaded!')
                    self.set_status('Ready', 'ready')

                    # Add system message to chat
                    self.add_message(
                        f"Uploaded: {filename}",
                        is_user=False,
                        is_system=True,
                    )
                else:
                    error = response.json().get('detail', 'Upload failed')
                    self.upload_status.set_text(f'Error: {error}')
                    self.set_status('Ready', 'ready')

        except Exception as e:
            self.upload_status.set_text(f'Error: {str(e)}')
            self.set_status('Ready', 'ready')

    async def send_message(self):
        """
        Send chat message, Non-blocking streaming, status updates show.
        """
        message = self.input_field.value.strip()

        if not message:
            return

        # Clear input
        self.input_field.value = ''
        self.send_button.disable()

        # Add user message
        self.add_message(message, is_user=True)

        try:
            # Update status - Searching
            self.set_status('Searching documents...', 'searching')

            # Prepare for assistant response
            assistant_msg_container = None
            assistant_msg_label = None

            async with httpx.AsyncClient(timeout=120.0) as client:
                # Update status - Generating
                self.set_status('Generating response...', 'generating')

                # Stream response
                async with client.stream(
                    'POST',
                    f'{BACKEND_URL}/api/chat/stream',
                    json={
                        'message': message,
                        'session_id': self.session_id,
                    },
                ) as response:
                    response.raise_for_status()

                    accumulated_response = ""

                    async for line in response.aiter_lines():
                        if line.startswith('data: '):
                            chunk = line[6:]

                            if chunk == '[DONE]':
                                break
                            elif chunk.startswith('[ERROR'):
                                self.add_message(
                                    f"Error: {chunk}", is_user=False, is_error=True)
                                break
                            else:
                                accumulated_response += chunk

                                # Create or update assistant message
                                if assistant_msg_container is None:
                                    with self.chat_container:
                                        assistant_msg_container = ui.card().classes('w-full bg-blue-50 p-3 mb-2')
                                        with assistant_msg_container:
                                            ui.label('Assistant').classes(
                                                'text-sm font-semibold text-blue-600 mb-1')
                                            assistant_msg_label = ui.label(accumulated_response).classes(
                                                'text-gray-800 whitespace-pre-wrap')
                                else:
                                    # Update existing message
                                    assistant_msg_label.set_text(
                                        accumulated_response)

                                # Scroll to bottom
                                await ui.run_javascript(
                                    f"document.getElementById('{self.chat_container.id}').scrollTop = "
                                    f"document.getElementById('{self.chat_container.id}').scrollHeight;"
                                )

            # Clear status
            self.set_status('Ready', 'ready')

        except Exception as e:
            self.add_message(f"Error: {str(e)}", is_user=False, is_error=True)
            self.set_status('Ready', 'ready')

        finally:
            self.send_button.enable()

    def add_message(self, text: str, is_user: bool = False, is_system: bool = False, is_error: bool = False):
        """Add message to chat.
        Args:
            text: Message content
            is_user: User message flag
            is_system: System message flag
            is_error: Error message flag
        """
        with self.chat_container:
            if is_error:
                card = ui.card().classes('w-full bg-red-50 p-3 mb-2')
                with card:
                    ui.label('Error').classes(
                        'text-sm font-semibold text-red-600 mb-1')
                    ui.label(text).classes('text-gray-800')
            elif is_system:
                card = ui.card().classes('w-full bg-green-50 p-3 mb-2')
                with card:
                    ui.label(text).classes('text-green-700 text-sm')
            elif is_user:
                card = ui.card().classes('w-full bg-gray-100 p-3 mb-2')
                with card:
                    ui.label('👤 You').classes(
                        'text-sm font-semibold text-gray-600 mb-1')
                    ui.label(text).classes('text-gray-800 whitespace-pre-wrap')
            else:
                pass

    def set_status(self, text: str, status_type: str = 'ready'):
        """Update status label.
        Args:
            text: Status text to display
            status_type: Type of status (ready, uploading, searching, generating)
        """
        color_map = {
            'ready': 'text-green-600',
            'uploading': 'text-blue-600',
            'processing': 'text-orange-600',
            'searching': 'text-purple-600',
            'generating': 'text-indigo-600',
        }

        color = color_map.get(status_type, 'text-gray-500')
        self.status_label.set_text(text)
        self.status_label.classes(replace=f'text-sm {color}')


# Create and run the interface, entry point it is
def create_chat_page():
    """Create chat page, NiceGUI app builds."""
    chat = ChatInterface()
    chat.create_ui()
