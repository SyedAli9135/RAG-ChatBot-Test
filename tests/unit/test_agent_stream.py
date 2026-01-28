import pytest
import pytest_check as check

from unittest.mock import patch, MagicMock

import app.agent.chat_agent as chat_agent_module
import app.knowledge.store as knowledge_module


# For asyncio testing purpose
class FakeChunk:
    def __init__(self, content):
        self.content = content


def fake_stream():
    for token in ["Hello", " ", "world", "!"]:
        yield FakeChunk(token)


@pytest.fixture(autouse=True)
def reset_singletons():
    chat_agent_module._agent_instance = None
    chat_agent_module._db = None
    knowledge_module._knowledge = None
    knowledge_module._contents_db = None
    yield
    chat_agent_module._agent_instance = None
    knowledge_module._knowledge = None


@pytest.mark.asyncio
@patch("app.agent.chat_agent.OpenAIChat")
@patch("app.agent.chat_agent.Agent")
@patch("app.knowledge.store.OpenAIEmbedder")
@patch("app.knowledge.store.LanceDb")
async def test_agent_can_stream(
    mock_lancedb,
    mock_embedder,
    MockAgent,
    MockOpenAIChat,
):
    # Mock knowledge
    fake_kb = MagicMock()
    fake_kb.search.return_value = []

    with patch("app.agent.chat_agent.get_knowledge", return_value=fake_kb):

        # Mock agent streaming
        mock_agent_instance = MagicMock()
        mock_agent_instance.run.return_value = fake_stream()
        MockAgent.return_value = mock_agent_instance

        agent = chat_agent_module.get_agent()

        chunks = []
        async for chunk in agent.stream_response("Say hello", "test"):
            chunks.append(chunk)

        check.equal("".join(chunks), "Hello world!")


@pytest.mark.asyncio
@patch("app.agent.chat_agent.OpenAIChat")
@patch("app.agent.chat_agent.Agent")
@patch("app.knowledge.store.OpenAIEmbedder")
@patch("app.knowledge.store.LanceDb")
async def test_agent_streaming_with_long_message(
    mock_lancedb,
    mock_embedder,
    MockAgent,
    MockOpenAIChat,
):
    fake_kb = MagicMock()
    fake_kb.search.return_value = []

    with patch("app.agent.chat_agent.get_knowledge", return_value=fake_kb):

        mock_agent_instance = MagicMock()
        mock_agent_instance.run.return_value = fake_stream()
        MockAgent.return_value = mock_agent_instance

        agent = chat_agent_module.get_agent()

        chunks = []
        async for chunk in agent.stream_response("Count to 10", "test2"):
            chunks.append(chunk)

        check.greater(len(chunks), 3)
