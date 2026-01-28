import io
import pytest
import pytest_check as check
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch

from app.main import app
from app.config import settings


@pytest.mark.asyncio
async def test_upload_pdf_success():
    """
    Test pdf uploads, sucessfully it is 
    """
    fake_pdf = io.BytesIO(b"%PDF-1.4 fake pdf content")

    with patch("app.api.file_upload_routes.add_pdf_to_knowledge") as mock_add:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/upload/pdf",
                files={"file": ("test.pdf", fake_pdf, "application/pdf")},
            )

        check.equal(response.status_code, 200)
        data = response.json()
        check.equal(data["status"], "completed")
        check.equal(data["filename"], "test.pdf")
        check.is_true("file_id" in data)
        mock_add.assert_called_once()


@pytest.mark.asyncio
async def test_upload_rejects_non_pdf():
    """
    Rejects non-pdf document, it is
    """
    fake_txt = io.BytesIO(b"hello")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/upload/pdf",
            files={"file": ("test.txt", fake_txt, "text/plain")},
        )

    check.equal(response.status_code, 400)
    check.is_true("Only PDF files" in response.json()["detail"])


@pytest.mark.asyncio
async def test_upload_rejects_empty_pdf():
    """
    Rejects empty pdf documents, it is
    """
    fake_pdf = io.BytesIO(b"")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/upload/pdf",
            files={"file": ("empty.pdf", fake_pdf, "application/pdf")},
        )

    check.equal(response.status_code, 400)
    check.is_true("cannot be empty" in response.json()["detail"])


@pytest.mark.asyncio
async def test_upload_rejects_large_file():
    """
    Rejects larger file than 10 mb, it is
    """
    big_content = b"x" * (settings.max_upload_size_mb * 1024 * 1024 + 1)
    fake_pdf = io.BytesIO(big_content)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/upload/pdf",
            files={"file": ("big.pdf", fake_pdf, "application/pdf")},
        )

    check.equal(response.status_code, 413)
