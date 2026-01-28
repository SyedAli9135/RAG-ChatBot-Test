import logging
from typing import AsyncGenerator
import asyncio

from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.openai import OpenAIChat

from app.knowledge.store import get_knowledge
from app.config import settings

logger = logging.getLogger(__name__)

# Global database instance for session/memory persistance
_db: SqliteDb | None = None


def get_db() -> SqliteDb:
    """
    Get or create database instance, singleton instance, it ensures.
    Returns:
        SqliteDb instance
    """
    global _db
    if _db is None:
        _db = SqliteDb(db_file="data/agno.db")
        logger.info("Database initialized")
    return _db


class ChatAgent:

    def __init__(self):
        """
        Initialize agent with openAI, database and knowledge it does.
        """
        db = get_db()
        self.knowledge = get_knowledge()

        model = OpenAIChat(
            id=settings.llm_model,
            api_key=settings.llm_api_key,
        )

        self.agent = Agent(
            name="RAG PDF Chatbot Agent",
            description="Helpful assistant, answers questions about uploaded PDFs",
            instructions=["You are a helpful AI assistant with access to uploaded PDF documents.",
                          "When answering questions, ALWAYS search and reference the knowledge base first.",
                          "If relevant information exists in the uploaded documents, cite it in your response.",
                          "If no relevant information is found in documents, say so clearly.",
                          ],
            model=model,
            db=db,
            knowledge=self.knowledge,
            enable_user_memories=True,
            search_knowledge=True,
            markdown=True
        )

        logger.info(f"Chat agent initialized with model: {settings.llm_model}")

    async def stream_response(
        self,
        message: str,
        session_id: str | None = None,
    ) -> AsyncGenerator[str, None]:
        """
        Stream response from agent, token by token, Agno handles 
        session history and knowledge search automatically.
        Args:
            message: User's question
            session_id: Session identifier
        Yields:
            Token chunks
        """
        try:
            logger.info(f"Streaming response for session: {session_id}")

            try:
                search_results = self.knowledge.search(message, max_results=3)

                # Build context for search results
                if search_results:
                    logger.info(
                        f"Found {len(search_results)} relevant documents")

                    context_parts = []
                    for i, doc in enumerate(search_results, 1):
                        if hasattr(doc, 'content'):
                            context_parts.append(
                                f"[Document {i}]\n{doc.content[:500]}")

                    context = "\n\n".join(context_parts)

                    enhanced_message = f"""Based on the following information from uploaded documents:
                        {context}

                        User question: {message}

                        Please answer the question using the information above."""

                else:
                    logger.info("No relevant documents found")
                    enhanced_message = message

            except Exception as e:
                logger.warning(f"Knowledge search failed: {e}")
                enhanced_message = message

            response_stream = self.agent.run(
                enhanced_message,
                user_id=session_id or "default",
                stream=True,
            )

            for chunk in response_stream:
                if hasattr(chunk, 'content') and chunk.content:
                    yield chunk.content
                    await asyncio.sleep(0)

        except Exception as e:
            logger.error(f"Error streaming response: {e}")
            yield f"\n[Error: {str(e)}]"


# Global agent instance
_agent_instance: ChatAgent | None = None


def get_agent() -> ChatAgent:
    """
    Get agent instance, singleton pattern it ensures.
    Returns:
        ChatAgent instance
    """
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = ChatAgent()
    return _agent_instance
