"""画像与行为域 - 用户认证相关 Schema."""

from datetime import datetime

from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    """用户注册请求."""

    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, max_length=128, description="密码")


class LoginRequest(BaseModel):
    """用户登录请求."""

    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=1, max_length=128)


class UserOut(BaseModel):
    """用户信息输出."""

    id: int
    username: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenOut(BaseModel):
    """登录成功返回的 Token."""

    access_token: str
    token_type: str = "bearer"
