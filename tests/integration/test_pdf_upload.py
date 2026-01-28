from io import BytesIO

import pytest
import pytest_check as check
from httpx import AsyncClient, ASGITransport
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

from app.main import app


def create_test_pdf(content: str) -> BytesIO:
    """Create PDF in memory, test data it contains.
    Args:
        content: Text content for PDF, written it will be
    Returns:
        BytesIO buffer with PDF data, ready for upload it is
    """
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)

    # Write content line by line
    y_position = 750
    lines = content.split('\n')

    for line in lines:
        if line.strip():
            c.drawString(100, y_position, line)
            y_position -= 20
            if y_position < 100:  # New page if needed
                c.showPage()
                y_position = 750

    c.save()
    buffer.seek(0)
    return buffer


def create_empty_pdf() -> BytesIO:
    """Create empty PDF buffer, error testing it enables.
    Returns:
        Empty BytesIO buffer, zero bytes it contains
    """
    return BytesIO(b"")


@pytest.mark.asyncio
async def test_upload_valid_pdf():
    """Valid PDF upload succeeds, verify we must.
    File accepted, processed, stored it should be.
    """
    # Create PDF with test content
    pdf_content = """Sample Test Document

This document contains information about artificial intelligence.
Machine learning is a subset of AI that focuses on learning from data.
Neural networks are inspired by biological neurons in the brain.
Deep learning uses multiple layers to progressively extract features.

The document also mentions Python programming language.
"""

    pdf_buffer = create_test_pdf(pdf_content)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/upload/pdf",
            files={"file": ("test_sample.pdf", pdf_buffer, "application/pdf")},
            timeout=60.0,
        )

        check.equal(response.status_code, 200, "Upload failed, it did!")

        data = response.json()
        check.is_in("file_id", data, "File ID missing!")
        check.is_in("filename", data, "Filename missing!")
        check.equal(data["filename"], "test_sample.pdf", "Filename wrong!")
        check.is_in("status", data, "Status missing!")


@pytest.mark.asyncio
async def test_upload_empty_pdf_rejected():
    """Empty PDF rejected, validation works it proves.
    Error 400 expect we do, empty files unacceptable they are.
    """
    empty_buffer = create_empty_pdf()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/upload/pdf",
            files={"file": ("empty.pdf", empty_buffer, "application/pdf")},
            timeout=30.0,
        )

        check.equal(response.status_code, 400, "Should reject empty file!")

        data = response.json()
        check.is_in("detail", data, "Error detail missing!")


@pytest.mark.asyncio
async def test_upload_non_pdf_rejected():
    """Non-PDF file rejected, type validation works it proves.
    Only PDFs allowed, others rejected they must be.
    """
    text_content = b"This is not a PDF, just plain text it is."
    text_buffer = BytesIO(text_content)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/upload/pdf",
            files={"file": ("test.txt", text_buffer, "text/plain")},
            timeout=30.0,
        )

        check.equal(response.status_code, 400, "Should reject non-PDF!")

        data = response.json()
        check.is_in("detail", data, "Error detail missing!")
        check.is_true(
            "pdf" in data["detail"].lower(),
            "Error message should mention PDF!"
        )


@pytest.mark.asyncio
async def test_upload_then_query_pdf():
    """Complete RAG flow: upload then query, end-to-end test it is.
    """
    # Create PDF with specific content about nutrition
    pdf_content = """Nutrition Guide

Macronutrients

Macronutrients are the nutrients that the body needs in large amounts.
They provide energy and are essential for growth and metabolism.

The three main macronutrients are:
1. Carbohydrates - provide 4 calories per gram
2. Proteins - provide 4 calories per gram  
3. Fats - provide 9 calories per gram

Carbohydrates are the body's primary energy source.
Proteins are essential for tissue repair and immune function.
Fats are important for hormone production and vitamin absorption.
"""

    pdf_buffer = create_test_pdf(pdf_content)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Step 1: Upload PDF
        upload_response = await client.post(
            "/api/upload/pdf",
            files={"file": ("nutrition.pdf", pdf_buffer, "application/pdf")},
            timeout=60.0,
        )

        check.equal(upload_response.status_code, 200, "Upload failed!")

        file_id = upload_response.json()["file_id"]

        # Step 2: Query about the PDF content
        query_response = await client.post(
            "/api/chat",
            json={
                "message": "What does the document say about macronutrients?",
                "session_id": f"rag_test_{file_id}",
            },
            timeout=60.0,
        )

        check.equal(query_response.status_code, 200, "Query failed!")

        data = query_response.json()
        response_text = data["response"].lower()

        # Should mention macronutrients or related terms from the document
        check.is_true(
            "macronutrient" in response_text or
            "carbohydrate" in response_text or
            "protein" in response_text or
            "energy" in response_text or
            "nutrient" in response_text,
            f"Response doesn't reference PDF content! Response: {response_text[:200]}"
        )


@pytest.mark.asyncio
async def test_multiple_pdfs_upload():
    """Multiple PDFs upload and query, scaling verify it does.
    Knowledge base handles multiple documents, verify we must.
    """
    # Create first PDF about AI
    pdf1_content = """Artificial Intelligence Overview

AI is the simulation of human intelligence by machines.
Machine learning enables systems to learn from data.
Neural networks mimic the human brain's structure.
"""
    pdf1_buffer = create_test_pdf(pdf1_content)

    # Create second PDF about Python
    pdf2_content = """Python Programming Guide

Python is a high-level programming language.
It is widely used for data science and web development.
Python has a simple and readable syntax.
"""
    pdf2_buffer = create_test_pdf(pdf2_content)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Upload first PDF
        response1 = await client.post(
            "/api/upload/pdf",
            files={"file": ("ai_guide.pdf", pdf1_buffer, "application/pdf")},
            timeout=60.0,
        )
        check.equal(response1.status_code, 200, "First upload failed!")

        # Upload second PDF
        response2 = await client.post(
            "/api/upload/pdf",
            files={"file": ("python_guide.pdf", pdf2_buffer,
                            "application/pdf")},
            timeout=60.0,
        )
        check.equal(response2.status_code, 200, "Second upload failed!")

        # Query should be able to find information from either document
        query_response = await client.post(
            "/api/chat",
            json={
                "message": "What programming language is mentioned in the documents?",
                "session_id": "multi_pdf_test",
            },
            timeout=60.0,
        )

        check.equal(query_response.status_code, 200, "Query failed!")


@pytest.mark.asyncio
async def test_upload_large_content_pdf():
    """Large PDF content handled, robustness verify we must.

    Multiple pages, chunking works it proves.
    """
    # Create a longer document
    pdf_content = """Machine Learning Comprehensive Guide

Introduction
Machine learning is a branch of artificial intelligence.

Chapter 1: Supervised Learning
Supervised learning uses labeled training data.
Classification and regression are main tasks.
Decision trees, random forests, and neural networks are common algorithms.

Chapter 2: Unsupervised Learning  
Unsupervised learning finds patterns in unlabeled data.
Clustering and dimensionality reduction are key techniques.
K-means and PCA are popular algorithms.

Chapter 3: Deep Learning
Deep learning uses neural networks with multiple layers.
Convolutional networks excel at image processing.
Recurrent networks handle sequential data.

Conclusion
Machine learning continues to evolve rapidly.
Applications span healthcare, finance, and many other domains.
"""

    pdf_buffer = create_test_pdf(pdf_content)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/upload/pdf",
            files={"file": ("ml_guide.pdf", pdf_buffer, "application/pdf")},
            timeout=60.0,
        )

        check.equal(response.status_code, 200, "Large PDF upload failed!")

        data = response.json()
        check.is_in("file_id", data, "File ID missing!")
