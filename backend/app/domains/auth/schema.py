from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    player_id: int
    pin: str = Field(..., min_length=4, max_length=4, pattern=r"^\d{4}$")
    remember_me: bool = False


class LoginResponse(BaseModel):
    access_token: str
    player_id: int
    player_name: str
    player_role: str
    is_admin: bool = False
    message: str = "로그인 성공"


class AdminLoginRequest(BaseModel):
    username: str
    password: str


class AdminLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    display_name: str
    is_admin: bool = True
