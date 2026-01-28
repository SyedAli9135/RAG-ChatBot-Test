import logging
from pathlib import Path

from agno.knowledge.knowledge import Knowledge
from agno.knowledge.embedder.openai import OpenAIEmbedder
from agno.knowledge.chunking.fixed import FixedSizeChunking
from agno.knowledge.reader.pdf_reader import PDFReader
from agno.vectordb.lancedb import LanceDb
from agno.db.sqlite import SqliteDb

from app.config import settings

logger = logging.getLogger(__name__)

# Global knowledge instance, singleton pattern
_knowledge: Knowledge | None = None

# Global contents database for tracking content status
_contents_db: SqliteDb | None = None


def get_contents_db() -> SqliteDb:
    """
    Get or create contents database
    Returns:
        SqliteDb instance
    """
    global _contents_db
    if _contents_db is None:
        _contents_db = SqliteDb(db_file="data/agno_contents.db")
        logger.info("Contents database initialized")
    return _contents_db


def get_knowledge() -> Knowledge:
    """
    Get or create knowledge base, stores PDF documents.
    LanceDB for vectors use
    Returns:
        Knowledge instance
    """
    global _knowledge
    if _knowledge is None:
        embedder = OpenAIEmbedder(
            id="text-embedding-3-small",
            api_key=settings.llm_api_key,
        )

        vector_db = LanceDb(
            table_name="pdf_knowledge",
            uri="data/lancedb",
            embedder=embedder,
        )

        contents_db = get_contents_db()

        _knowledge = Knowledge(
            name="PDF Documents",
            vector_db=vector_db,
            contents_db=contents_db,
            max_results=5,
        )

        logger.info("Knowledge base initialized with LanceDB")

    return _knowledge


def get_pdf_reader() -> PDFReader:
    """
    Get PDF reader with chunking strategy
    Returns:
        PDFReader instance
    """
    return PDFReader(
        chunking_strategy=FixedSizeChunking(
            chunk_size=1000,
        ),
    )


def add_pdf_to_knowledge(file_path: str | Path, filename: str, document_id: str) -> None:
    """
    Add PDF to knowledge base, make it searchable.
    Reader parses, knowledge stores, Agno handles vectorization.
    Args:
        file_path: Path to PDF file, read we shall
        document_id: Unique identifier, tracking allows
    """
    try:
        knowledge = get_knowledge()
        reader = get_pdf_reader()

        # Load and parse PDF document
        # Reader chunks, knowledge vectorizes and stores
        knowledge.add_content(
            path=str(file_path),
            reader=reader,
            metadata={
                "filename": filename,
                "file_id": document_id,
                "type": "pdf",
            },
        )

        logger.info(f"PDF added to knowledge base: {document_id}")
    except Exception as e:
        logger.error(f"Error adding PDF to knowledge: {e}")
        raise
