from pydantic import BaseModel, Field


class SkillResponse(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}

class CreateSkillRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)