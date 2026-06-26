from pydantic import BaseModel


class SkillResponse(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}
