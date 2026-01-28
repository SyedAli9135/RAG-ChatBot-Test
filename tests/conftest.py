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
