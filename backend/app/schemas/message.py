from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class MessageResponse(BaseModel):
    id: int
    match_id: int
    sender_id: int
    content: str
    is_read: bool
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class WSMessageIn(BaseModel):
    type: str = "message"
    content: str


class WSMessageOut(BaseModel):
    type: str = "message"
    id: int
    match_id: int
    sender_id: int
    content: str
    created_at: datetime
