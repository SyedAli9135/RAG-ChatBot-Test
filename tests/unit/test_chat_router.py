import pytest
import pytest_check as check
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, MagicMock

from app.main import app


async def async_generator_mock(items):
    """
    Helper to create proper async generator, testing needs it.
    Args:
        items: List of items to yield
    Yields:
        Items one by one, async generator it is
    """
    for item in items:
        yield item


@pytest.mark.asyncio
async def test_chat_stream_endpoint():
    """
    Streaming endpoint test, mock agent use we do.
    SSE format verify, multiple chunks confirm we must.
    """
    fake_tokens = ["Hello", " ", "world", "!"]

    mock_agent = MagicMock()

    mock_agent.stream_response = lambda message, session_id=None: async_generator_mock(
        fake_tokens)

    with patch("app.api.chat_routes.get_agent", return_value=mock_agent):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            request_data = {"message": "Hi there", "session_id": "test123"}

            # Use streaming response
            chunks = []
            async with client.stream("POST", "/api/chat/stream", json=request_data) as response:
                check.equal(response.status_code, 200,
                            "Status code wrong, it is!")

                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        chunk = line[6:]
                        chunks.append(chunk)

            check.is_in("Hello", chunks, "First token missing!")
            check.is_in(" ", chunks, "Space missing!")
            check.is_in("world", chunks, "Third token missing!")
            check.is_in("!", chunks, "Exclamation missing!")
            check.is_in("[DONE]", chunks, "Done signal missing!")


@pytest.mark.asyncio
async def test_chat_non_stream_endpoint():
    """
    Non-streaming endpoint test, complete response verify we must.
    Agent mock use, response accumulation test it does.
    """
    fake_tokens = ["Hello", " ", "world", "!"]

    mock_agent = MagicMock()
    mock_agent.stream_response = lambda message, session_id=None: async_generator_mock(
        fake_tokens)

    with patch("app.api.chat_routes.get_agent", return_value=mock_agent):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            request_data = {"message": "Hi there", "session_id": "test456"}
            response = await client.post("/api/chat", json=request_data)

        check.equal(response.status_code, 200, "Status code wrong, it is!")

        data = response.json()
        check.equal(data["response"], "Hello world!", "Response wrong!")
        check.equal(data["session_id"], "test456", "Session ID wrong!")


@pytest.mark.asyncio
async def test_chat_stream_with_empty_message():
    """
    Empty message rejected, validation works it proves.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/chat/stream",
            json={"message": "", "session_id": "test"}
        )

    check.equal(response.status_code, 422, "Should reject empty message!")


@pytest.mark.asyncio
async def test_chat_non_stream_with_empty_message():
    """
    Empty message rejected in non-stream endpoint too.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/chat",
            json={"message": "", "session_id": "test"}
        )

    check.equal(response.status_code, 422, "Should reject empty message!")
