from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List

class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class ChatBotQuery(BaseModel):
    session_id: str
    user_id: Optional[int] = None
    query_text: str

class ChatBotLogResponse(BaseSchema):
    chatbot_id: int
    session_id: str
    user_id: Optional[int]
    query_text: str
    response_text: str
    timestamp: datetime