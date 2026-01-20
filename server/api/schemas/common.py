"""
通用响应模型
"""
from pydantic import BaseModel, Field


class MessageResponse(BaseModel):
    """通用消息响应模型"""
    message: str
    success: bool = True


class ErrorResponse(BaseModel):
    """错误响应模型"""
    error: str
    detail: str | None = None
    success: bool = False