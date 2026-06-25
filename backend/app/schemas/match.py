from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class MatchResponse(BaseModel):
    id: int
    user_id: int
    project_id: int
    swipe_id: int
    status: str
    created_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
