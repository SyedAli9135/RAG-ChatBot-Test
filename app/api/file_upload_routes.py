import asyncio
import concurrent.futures
import logging
import uuid
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse

from app.config import settings
from app.knowledge.store import add_pdf_to_knowledge, get_knowledge, get_pdf_reader

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/upload", tags=["upload"])

UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/pdf")
async def upload_pdf(file: UploadFile = File(...)) -> JSONResponse:
    """
    Upload PDF file, to knowledge base.
    Validation performs: type, size, emptiness checks.
    Args:
        file: PDF file uploaded
    Returns:
        JSON response with file ID and status
    """

    file_path: Path | None = None

    # Validate file type
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed",
        )

    try:
        # Read file content
        content = await file.read()

        if len(content) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File cannot be empty",
            )

        # Size limit check
        max_size = settings.max_upload_size_mb * 1024 * 1024
        if len(content) > max_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds maximum limit of {settings.max_upload_size_mb}MB",
            )

        file_id = str(uuid.uuid4())
        file_path = UPLOAD_DIR / f"{file_id}_{file.filename}"

        with open(file_path, "wb") as f:
            f.write(content)

        logger.info(f"File saved: {file_path}")

        # Add to knowledge base in thread pool
        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            await loop.run_in_executor(
                executor,
                lambda: add_pdf_to_knowledge(
                    file_path=file_path,
                    document_id=file_id,
                    filename=file.filename,
                ),
            )

        logger.info(f"PDF processed successfully: {file_id}")

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": "PDF uploaded and processed successfully",
                "file_id": file_id,
                "filename": file.filename,
                "status": "completed",
            },
        )

    except HTTPException:
        if file_path and file_path.exists():
            try:
                file_path.unlink()
            except OSError:
                pass
        raise

    except Exception as e:
        if file_path and file_path.exists():
            try:
                file_path.unlink()
            except OSError:
                pass

        logger.error(f"Error processing PDF: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload PDF: {str(e)}",
        )
