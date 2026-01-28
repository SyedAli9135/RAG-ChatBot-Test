import pytest
import pytest_check as check
from httpx import AsyncClient
from httpx import ASGITransport

from app.main import app


@pytest.mark.asyncio
async def test_streaming_endpoint_returns_multiple_chunks():
    """
    Streaming endpoint multiple chunks returns
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        request_data = {
            "message": "Count from 1 to 5, one number at a time",
            "session_id": "test_stream_123",
        }

        # Stream the response
        chunks = []
        async with client.stream(
            "POST",
            "/api/chat/stream",
            json=request_data,
            timeout=60.0,
        ) as response:
            check.equal(response.status_code, 200, "Status code is wrong!")

            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    chunk = line[6:]
                    if chunk and chunk not in ["[DONE]", ""]:
                        if not chunk.startswith("[ERROR"):
                            chunks.append(chunk)

        check.greater(
            len(chunks),
            3,
            f"Only {len(chunks)} chunk(s) received! Real streaming requires multiple chunks!"
        )

        full_response = "".join(chunks)
        check.greater(len(full_response), 0,
                      "Empty response!")


@pytest.mark.asyncio
async def test_streaming_endpoint_with_short_message():
    """
    Short message streaming
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        request_data = {
            "message": "Say hi",
            "session_id": "test_short_stream",
        }

        chunks = []
        async with client.stream(
            "POST",
            "/api/chat/stream",
            json=request_data,
            timeout=60.0,
        ) as response:
            check.equal(response.status_code, 200, "Status code is wrong!")

            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    chunk = line[6:]
                    if chunk and chunk not in ["[DONE]", ""]:
                        if not chunk.startswith("[ERROR"):
                            chunks.append(chunk)

        check.greater(len(chunks), 0, "No chunks received!")


@pytest.mark.asyncio
async def test_non_streaming_endpoint():
    """
    Non-streaming endpoint works
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/chat",
            json={
                "message": "Say hello in one sentence",
                "session_id": "test_simple_123",
            },
            timeout=60.0,
        )

        check.equal(response.status_code, 200, "Status code is wrong!")

        data = response.json()
        check.is_in("response", data, "Response field missing!")
        check.is_in("session_id", data, "Session ID missing!")
        check.greater(len(data["response"]), 0,
                      "Empty response!")


@pytest.mark.asyncio
async def test_streaming_with_invalid_request():
    """
    Invalid request handled gracefully
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/chat/stream",
            json={
                "message": "",
                "session_id": "test_invalid",
            },
            timeout=30.0,
        )

        check.equal(response.status_code, 422,
                    "Should reject empty message, it should!")


@pytest.mark.asyncio
async def test_session_continuity():
    """
    Session maintains conversation history
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        session_id = "test_session_memory_456"

        response1 = await client.post(
            "/api/chat",
            json={
                "message": "Remember: my favorite number is 42",
                "session_id": session_id,
            },
            timeout=60.0,
        )
        check.equal(response1.status_code, 200, "First request failed!")

        response2 = await client.post(
            "/api/chat",
            json={
                "message": "What is my favorite number?",
                "session_id": session_id,
            },
            timeout=60.0,
        )
        check.equal(response2.status_code, 200, "Second request failed!")

        data = response2.json()
        response_text = data["response"].lower()

        check.is_true(
            "42" in response_text or "forty" in response_text,
            f"Memory not working! Response: {response_text}"
        )


@pytest.mark.asyncio
async def test_different_sessions_isolated():
    """
    Different sessions isolated
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Session A
        await client.post(
            "/api/chat",
            json={
                "message": "My name is Alice",
                "session_id": "session_a",
            },
            timeout=60.0,
        )

        # Session B
        response = await client.post(
            "/api/chat",
            json={
                "message": "What is my name?",
                "session_id": "session_b",
            },
            timeout=60.0,
        )

        data = response.json()
        response_text = data["response"].lower()

        check.is_false(
            "alice" in response_text,
            f"Sessions not isolated! Response: {response_text}"
        )
