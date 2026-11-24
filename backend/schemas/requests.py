"""Pydantic 请求/响应模型 — 统一输入校验"""

from pydantic import BaseModel, Field
from typing import Optional


class RegisterIn(BaseModel):
    username: str = Field(min_length=2, max_length=30, description="2-30 字符")
    password: str = Field(min_length=4, description="至少 4 位")
    email: Optional[str] = None
    target_language: Optional[str] = "en"


class LoginIn(BaseModel):
    username: str
    password: str


class CompleteLessonIn(BaseModel):
    lesson_id: int
    score: int = 0
    minutes_spent: int = 15


class PostIn(BaseModel):
    content: str = Field(min_length=1, max_length=500)
    category: Optional[str] = "general"


class RecommendIn(BaseModel):
    language_code: str


class ApiMessage(BaseModel):
    ok: bool = True
    message: Optional[str] = None
