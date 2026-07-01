from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class ProjectMessageSenderResponse(BaseModel):
    id: int
    full_name: str
    avatar_file_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)

class ProjectMessageResponse(BaseModel):
    id: int
    project_id: int
    sender_id: int
    content: str
    created_at: datetime
    sender: Optional[ProjectMessageSenderResponse] = None

    model_config = ConfigDict(from_attributes=True)

class ProjectMessageCreateRequest(BaseModel):
    content: str = Field(min_length=1, max_length=4000)

class WSProjectMessageIn(BaseModel):
    type: str = Field("message", pattern=r"^message$")
    content: str = Field(min_length=1, max_length=4000)

class WSProjectMessageOut(BaseModel):
    type: str = "message"
    id: int
    project_id: int
    sender_id: int
    content: str
    created_at: datetime
    sender: Optional[ProjectMessageSenderResponse] = None

    model_config = ConfigDict(from_attributes=True)