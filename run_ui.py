from nicegui import ui
from app.ui.chat_interface import create_chat_page

create_chat_page()

ui.run(
    title='RAG Chatbot',
    port=8080,
    reload=True,
    show=True,
)
