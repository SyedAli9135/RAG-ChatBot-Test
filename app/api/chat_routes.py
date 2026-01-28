import logging
from typing import AsyncGenerator

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.agent.chat_agent import get_agent
from app.api.models import ChatRequest

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat/stream")
async def stream_chat(request: ChatRequest) -> StreamingResponse:
    """
    Stream chat response
    Args:
        request: Chat request with message
    Returns:
        StreamingResponse with text/event-stream
    """
    try:
        agent = get_agent()

        async def generate() -> AsyncGenerator[str, None]:
            """
            Generate streaming response, yields chunks with SSE format, browsers understand they do.
            """
            try:
                async for token in agent.stream_response(
                    message=request.message,
                    session_id=request.session_id,
                ):
                    yield f"data: {token}\n\n"

                yield "data: [DONE]\n\n"

            except Exception as e:
                logger.error(f"Error in stream generation: {e}")
                yield f"data: [ERROR: {str(e)}]\n\n"

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

    except Exception as e:
        logger.error(f"Error in stream_chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat")
async def chat(request: ChatRequest) -> dict[str, str]:
    """
    Non-streaming chat endpoint
    Args:
        request: Chat request
    Returns:
        Complete response
    """
    try:
        agent = get_agent()

        response_text = ""
        async for token in agent.stream_response(
            message=request.message,
            session_id=request.session_id,
        ):
            response_text += token

        return {
            "response": response_text,
            "session_id": request.session_id or "default",
        }

    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))
