from unittest.mock import patch, MagicMock
from pathlib import Path
import pytest_check as check

from app.knowledge.store import add_pdf_to_knowledge, get_pdf_reader


def test_pdf_reader_initialization():
    """
    PDF reader creates correctly, it is
    """
    reader = get_pdf_reader()
    check.is_not_none(reader)
    check.is_not_none(reader.chunking_strategy)


def test_add_pdf_to_knowledge_calls_vector_store():
    """
    Adds pdf knowledge to vector store mock, it is
    """
    fake_knowledge = MagicMock()
    fake_reader = MagicMock()

    with patch("app.knowledge.store.get_knowledge", return_value=fake_knowledge), \
            patch("app.knowledge.store.get_pdf_reader", return_value=fake_reader):

        add_pdf_to_knowledge(
            file_path=Path("dummy.pdf"),
            filename="dummy.pdf",
            document_id="123",
        )

        fake_knowledge.add_content.assert_called_once()

        args, kwargs = fake_knowledge.add_content.call_args
        check.equal(kwargs["metadata"]["filename"], "dummy.pdf")
        check.equal(kwargs["metadata"]["file_id"], "123")
        check.equal(kwargs["metadata"]["type"], "pdf")
