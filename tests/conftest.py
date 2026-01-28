import pytest

from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """Test client fixture, for API testing use it you shall.

    Returns:
        TestClient instance, ready for requests it is.
    """
    return TestClient(app)


def pytest_configure(config):
    """Configure pytest for async tests, proper setup it ensures."""
    config.option.asyncio_mode = "auto"
