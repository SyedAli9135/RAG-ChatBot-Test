from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """
    Chat request model, parameters of api, it is
    """

    message: str = Field(..., min_length=1,
                         description="User message should not be empty")
    session_id: str | None = Field(
        None, description="Session ID to maintain continuity")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "message": "What is the meaning of life?",
                    "session_id": "session_123"
                }
            ]
        }
    }


class ChatResponse(BaseModel):
    """
    Chat response model, response paramaters of api, it is
    """

    response: str = Field(...,
                          description="Agent's response")
    session_id: str = Field(...,
                            description="Session identifier")


class StatusUpdate(BaseModel):
    """
    Status update model
    For async operations, to keep user informed.
    """

    status: str = Field(...,
                        description="Current status")
    message: str | None = Field(
        None, description="Additional details")
