import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.chat_routes import router as chat_router
from app.api.file_upload_routes import router as upload_router

from app.config import settings

# Logging configuration
logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# App initialization
app = FastAPI(
    title="RAG Chatbot API",
    description="A chatbot with RAG capabilities, wise and helpful it is.",
    version="0.1.0"
)

# Cors Middleware support
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routes
app.include_router(chat_router)
app.include_router(upload_router)


@app.get("/")
async def root():
    """
    Root endpoint.
    Returns:
        Simple message, to confirm operational the API is.
    """
    return {
        "message": "RAG Chatbot API is running. Much wisdom, it has.",
        "version": "0.1.0",
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint, status of system report it does.
    Returns:
        Health status, for monitoring useful it is.
    """
    return {
        "status": "healthy",
        "llm_model": settings.llm_model,
        "max_upload_size_mb": settings.max_upload_size_mb,
    }
