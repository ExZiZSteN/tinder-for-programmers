from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(
        min_length=8,
        max_length=128,
        description="Минимум 8 символов. Bcrypt обрежет до 72 байт",
    )
    full_name: str = Field(
        min_length=1,
        max_length=150,
        description="Полное имя пользователя",
    )


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field (
        min_length=1,
        max_length=128,
    )


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user_id: int
