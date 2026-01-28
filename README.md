# RAG Chatbot with FastAPI, Agno, and NiceGUI

A production-ready Retrieval-Augmented Generation (RAG) chatbot that allows users to upload PDF documents and ask questions about them. Built with modern Python frameworks and featuring real-time streaming responses.

## Features

- **Real-time Streaming**: Token-by-token response streaming for smooth user experience
- **PDF Intelligence**: Upload PDFs and ask questions about their content
- **Vector Search**: Semantic search using LanceDB and OpenAI embeddings
- **Interactive UI**: Clean NiceGUI interface with async status updates
- **Fully Tested**: Comprehensive unit and integration tests

## Architecture
        ┌───────────────────────────┐
        │       NiceGUI Frontend     │  (Port 8080)
        │ ┌───────────────────────┐ │
        │ │ Chat UI / PDF Upload   │ │
        │ │ Status & Notifications │ │
        │ └───────────────────────┘ │
        └───────────────┬───────────┘
                        │ HTTP / WebSocket
                        ▼
        ┌───────────────────────────┐
        │       FastAPI Backend      │  (Port 8000)
        │ ┌───────────────────────┐ │
        │ │ REST / SSE Endpoints   │ │
        │ │ Upload / Chat / Stream │ │
        │ └─────────┬─────────────┘ │
        └───────────│────────────────┘
                    │
                    ▼
        ┌───────────────────────────┐
        │        Chat Orchestrator   │
        │       (Agno / Agent Layer) │
        │ ┌───────────────────────┐ │
        │ │ LLM / Retrieval Agent  │ │
        │ │ Streaming Response     │ │
        │ └─────────┬─────────────┘ │
        └───────────│────────────────┘
                    │
        ┌────────┴────────┐
        ▼                 ▼
        ┌─────────────┐   ┌─────────────┐
        │ PDF Parser  │   │ Vector DB    │
        │ (PyPDF2)    │   │ (LanceDB)   │
        │ Text Extract│   │ Embeddings  │
        └─────────────┘   └─────────────┘


### Key Design Decisions

1. **RAG Implementation**: Relying on Agno's automatic knowledge search
2. **LanceDB over PostgreSQL**: File-based vector database for simplicity - no separate database server needed
3. **Streaming-First**: All chat responses stream token-by-token for better UX
4. **Session-Based Memory**: Agno's built-in session management for conversation continuity

## Prerequisites

- Python 3.13 or higher
- OpenAI API key 
- 2GB free disk space

## Quick Start

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd rag-chatbot
```

### 2. Set Up Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Mac/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your API key
```

**Edit `.env`:**
```env
# For OpenAI (paid)
llm_api_key=sk-your-openai-api-key-here

### 5. Run the Application

**Terminal 1 - Start Backend:**
```bash
python run.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Terminal 2 - Start Frontend:**
```bash
python run_ui.py
```

You should see:
```
NiceGUI ready to go on http://localhost:8080
```

### 6. Open Your Browser

Go to: **http://localhost:8080**

You should see the chat interface!

## Usage Guide

### Upload a PDF

1. Click **"Choose PDF"** button
2. Select a PDF file from your computer
3. Wait for "Uploaded" message
4. PDF content is now searchable!

### Ask Questions

1. Type your question in the input field
2. Press Enter or click **"Send"**
3. Watch the response stream in real-time!
4. The agent will search the uploaded PDFs and provide relevant answers

### Example Conversation
```
You: What is this document about?
🤖: Based on the uploaded document, it discusses...

You: Can you summarize the key points?
🤖: The main points are: 1) ... 2) ... 3) ...
```

## 🧪 Running Tests

### Run All Tests
```bash
run ./run_tests.sh 
```

### Run Specific Test Suites
```bash
# Unit tests only
pytest tests/unit/ -v

# Integration tests only
pytest tests/integration/ -v

```

## Project Structure
```
rag-chatbot/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config.py            # Pydantic settings
│   │
│   ├── agent/               # Chat agent logic
│   │   ├── __init__.py
│   │   └── chat_agent.py    # Agno agent with streaming
│   │
│   ├── api/                 # API endpoints
│   │   ├── __init__.py
│   │   ├── models.py        # Pydantic models
│   │   ├── chat_routes.py        # Chat endpoints
│   │   └── file_upload_routes.py        # PDF upload endpoint
│   │
│   ├── knowledge/           # Knowledge management
│   │   ├── __init__.py
│   │   └── store.py         # LanceDB vector store
│   │
│   └── ui/                  # NiceGUI interface
│       ├── __init__.py
│       └── chat_interface.py
│
├── tests/
│   ├── conftest.py          # Pytest configuration
│   ├── unit/                # Unit tests
│   └── integration/         # Integration tests
│
├── data/                    # Runtime data (gitignored)
│   ├── uploads/             # Temporary PDF storage
│   ├── lancedb/             # Vector database
│   └── *.db                 # SQLite databases
│
├── .env                     # Your API keys (gitignored)
├── .env.example             # Environment template
├── .cursorrules             # Cursor IDE rules
├── requirements.txt         # dependencies
├── run.py                   # Backend runner
├── run_ui.py               # Frontend runner
└── README.md               # This file
```

## Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Backend** | FastAPI | Async web framework |
| **Agent** | Agno | LLM orchestration & session management |
| **LLM** | OpenAI API | Language model (GPT-3.5/4 or compatible) |
| **Vector DB** | LanceDB | File-based vector storage |
| **Embeddings** | OpenAI | Text embeddings for semantic search |
| **PDF Parser** | PyPDF2 | Extract text from PDFs |
| **Frontend** | NiceGUI | Python-based web UI |
| **Testing** | pytest | Test framework |
| **Type Checking** | Pydantic | Runtime type validation |

## Cursor IDE Configuration

This project is optimized for use with Cursor IDE:

### Features Configured

1. **MCP Servers**: Documentation for Agno, FastAPI, and NiceGUI
2. **Code Style Rules**: Modern Python typing, Pydantic models
3. **Linting**: Ruff for fast Python linting
4. **Formatting**: Black for consistent code style
5. **Testing**: pytest integration with async support

### How It Helped

- **Auto-completion** from framework documentation
- **Type error catching** before running code
- **Consistent style** across all files
- **Quick refactoring** with intelligent suggestions

See `.cursorrules` for detailed configuration.

## 🔧 Configuration Options

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `llm_api_key` | *(required)* | Your OpenAI or compatible API key |


## 📝 API Documentation

### Interactive API Docs

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Welcome message |
| GET | `/health` | Health check |
| POST | `/api/chat` | Non-streaming chat |
| POST | `/api/chat/stream` | Streaming chat (SSE) |
| POST | `/api/upload/pdf` | Upload PDF document |

## 🐛 Troubleshooting

### Issue: "Module not found"
**Solution:**
```bash
# Make sure venv is activated
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements-dev.txt
```

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## License

This project is licensed under the MIT License.

## Acknowledgments

- **Agno** for excellent agent orchestration
- **FastAPI** for modern async Python web framework
- **NiceGUI** for Python-based UI framework
- **LanceDB** for simple vector database solution

## Support

For questions or issues:
1. Check this README thoroughly
2. Review the code comments
3. Check existing GitHub issues
4. Create a new issue with details
