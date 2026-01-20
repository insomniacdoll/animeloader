"""
健康检查API路由
"""
from fastapi import APIRouter
from server.api.schemas import MessageResponse
from datetime import datetime


router = APIRouter(prefix="/health", tags=["健康检查"])


@router.get(
    "",
    response_model=MessageResponse,
    summary="健康检查",
    description="检查服务是否正常运行"
)
def health_check():
    """健康检查端点"""
    return MessageResponse(
        message="AnimeLoader server is running",
        success=True
    )