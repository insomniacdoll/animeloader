"""
链接相关扩展API路由（下载任务）
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from server.database import get_db
from server.services.download_service import DownloadService
from server.api.schemas import (
    DownloadTaskListResponse,
    DownloadTaskResponse,
    MessageResponse
)
from server.api.auth import verify_api_key


# 在路由器级别添加认证依赖
router = APIRouter(
    prefix="/links",
    tags=["链接扩展"],
    dependencies=[Depends(verify_api_key)]
)


def get_download_service(db: Session = Depends(get_db)) -> DownloadService:
    """获取下载服务实例"""
    return DownloadService(db)


@router.get(
    "/{link_id}/downloads",
    response_model=DownloadTaskListResponse,
    summary="获取链接的下载任务",
    description="获取链接的所有下载任务"
)
def get_link_downloads(
    link_id: int,
    download_service: DownloadService = Depends(get_download_service)
):
    """获取链接的下载任务"""
    tasks = download_service.get_download_tasks_by_link(link_id)
    return DownloadTaskListResponse(
        total=len(tasks),
        items=[DownloadTaskResponse.model_validate(task) for task in tasks],
        skip=0,
        limit=len(tasks)
    )