from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    match_id: int
    sender_id: int
    content: str
    is_read: bool
    read_at: Optional[datetime] = None
    created_at: datetime


class MessageCreateRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=4000)


class WSMessageIn(BaseModel):
    """Схема входящего сообщения от клиента по WebSocket"""
    type: str = Field("message", pattern=r"^message$")
    content: str = Field(..., min_length=1, max_length=4000)


class WSMessageOut(BaseModel):
    """Схема исходящего сообщения клиентам по WebSocket"""
    model_config = ConfigDict(from_attributes=True)

    type: str = "message"
    id: int
    match_id: int
    sender_id: int
    content: str
    is_read: bool = False
    created_at: datetime
