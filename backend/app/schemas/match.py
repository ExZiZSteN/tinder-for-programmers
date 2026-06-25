from datetime import datetime
from typing import Optional
from app.models.match import MatchStatus
from pydantic import BaseModel

class MatchResponse(BaseModel):
    id: int
    user_id: int
    project_id: int
    swipe_id: int
    status: MatchStatus
    created_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
