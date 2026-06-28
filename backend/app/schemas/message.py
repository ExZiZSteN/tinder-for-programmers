from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class MessageResponse(BaseModel):
    id: int
    match_id: int
    sender_id: int
    content: str
    is_read: bool
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
    
class MessageCreateRequest(BaseModel):
    content: str = Field(min_length=1, max_length=1000)

class WSMessageIn(BaseModel):
    type: str = Field("message", pattern=r"^message$")
    content: str = Field(
        min_length=1,
        max_length=4000,
    )


class WSMessageOut(BaseModel):
    type: str = "message"
    id: int
    match_id: int
    sender_id: int
    content: str
    created_at: datetime
