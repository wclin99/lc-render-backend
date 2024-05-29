from pydantic import BaseModel
from typing import Optional
from enum import Enum, IntEnum

class ApiDocTags(str, Enum):
    app = 'Application'
    chat_session="Chat session"
    Chat_history="Chat history"

class ChatRole(str, Enum):
    system = "system"
    ai = "ai"
    human = "human"

class ResponseModel(BaseModel):
    success: bool
    status_code: int
    error: Optional[str] = None
    data: Optional[dict] = None
