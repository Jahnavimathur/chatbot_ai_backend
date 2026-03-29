from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum

class RoleEnum(str, Enum):
    user = "user"
    assistant = "assistant"

class MessageBase(BaseModel):
    role: RoleEnum
    content: str
    
class MessageCreate(MessageBase):
    pass
    
class Message(MessageBase):
    id: int
    session_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class ChatSessionBase(BaseModel):
    title: str
    
class ChatSessionCreate(ChatSessionBase):
    pass
    
class ChatSession(ChatSessionBase):
    id: int
    user_id: int
    created_at: datetime
    messages: List[Message] = []
    
    class Config:
        from_attributes = True

# Used for the POST /chat endpoint
class ChatRequest(BaseModel):
    session_id: int
    message: str
