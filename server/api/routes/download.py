"""
下载任务相关API路由
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from server.database import get_db
from server.services.download_service import DownloadService
from server.api.schemas import (
    DownloadTaskCreate,
    DownloadTaskResponse,
    DownloadTaskListResponse,
    DownloadStatusResponse,
    MessageResponse
)


router = APIRouter(prefix="/downloads", tags=["下载任务"])


def get_download_service(db: Session = Depends(get_db)) -> DownloadService:
    """获取下载服务实例"""
    return DownloadService(db)


@router.get(
    "",
    response_model=DownloadTaskListResponse,
    summary="获取所有下载任务",
    description="获取所有下载任务列表"
)
def get_downloads(
    rss_source_id: Optional[int] = Query(None, description="RSS源ID"),
    status: Optional[str] = Query(None, description="任务状态"),
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回的记录数"),
    download_service: DownloadService = Depends(get_download_service)
):
    """获取所有下载任务"""
    total = download_service.count_download_tasks(
        rss_source_id=rss_source_id,
        status=status
    )
    tasks = download_service.get_download_tasks(
        rss_source_id=rss_source_id,
        status=status,
        skip=skip,
        limit=limit
    )
    
    return DownloadTaskListResponse(
        total=total,
        items=[DownloadTaskResponse.model_validate(task) for task in tasks],
        skip=skip,
        limit=limit
    )


@router.get(
    "/active",
    response_model=DownloadTaskListResponse,
    summary="获取活跃的下载任务",
    description="获取所有活跃的下载任务"
)
def get_active_downloads(
    download_service: DownloadService = Depends(get_download_service)
):
    """获取活跃的下载任务"""
    tasks = download_service.get_active_downloads()
    return DownloadTaskListResponse(
        total=len(tasks),
        items=[DownloadTaskResponse.model_validate(task) for task in tasks],
        skip=0,
        limit=len(tasks)
    )


@router.get(
    "/{task_id}",
    response_model=DownloadTaskResponse,
    summary="获取单个下载任务",
    description="根据ID获取单个下载任务的详细信息"
)
def get_download_task(
    task_id: int,
    download_service: DownloadService = Depends(get_download_service)
):
    """获取单个下载任务"""
    task = download_service.get_download_task(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"下载任务ID {task_id} 不存在"
        )
    return DownloadTaskResponse.model_validate(task)


@router.post(
    "",
    response_model=DownloadTaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建下载任务",
    description="创建新的下载任务"
)
def create_download_task(
    task_data: DownloadTaskCreate,
    download_service: DownloadService = Depends(get_download_service)
):
    """创建下载任务"""
    task = download_service.create_download_task(
        link_id=task_data.link_id,
        rss_source_id=0,  # 需要从链接获取
        downloader_id=task_data.downloader_id,
        file_path=task_data.file_path
    )
    if not task:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="创建下载任务失败"
        )
    return DownloadTaskResponse.model_validate(task)


@router.post(
    "/{task_id}/start",
    response_model=DownloadTaskResponse,
    summary="开始下载",
    description="开始下载任务"
)
def start_download(
    task_id: int,
    download_service: DownloadService = Depends(get_download_service)
):
    """开始下载"""
    task = download_service.start_download(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"下载任务ID {task_id} 不存在"
        )
    return DownloadTaskResponse.model_validate(task)


@router.post(
    "/{task_id}/pause",
    response_model=DownloadTaskResponse,
    summary="暂停下载",
    description="暂停下载任务"
)
def pause_download(
    task_id: int,
    download_service: DownloadService = Depends(get_download_service)
):
    """暂停下载"""
    task = download_service.pause_download(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"下载任务ID {task_id} 不存在"
        )
    return DownloadTaskResponse.model_validate(task)


@router.post(
    "/{task_id}/resume",
    response_model=DownloadTaskResponse,
    summary="恢复下载",
    description="恢复下载任务"
)
def resume_download(
    task_id: int,
    download_service: DownloadService = Depends(get_download_service)
):
    """恢复下载"""
    task = download_service.resume_download(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"下载任务ID {task_id} 不存在"
        )
    return DownloadTaskResponse.model_validate(task)


@router.post(
    "/{task_id}/cancel",
    response_model=DownloadTaskResponse,
    summary="取消下载",
    description="取消下载任务"
)
def cancel_download(
    task_id: int,
    download_service: DownloadService = Depends(get_download_service)
):
    """取消下载"""
    task = download_service.cancel_download(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"下载任务ID {task_id} 不存在"
        )
    return DownloadTaskResponse.model_validate(task)


@router.get(
    "/{task_id}/status",
    response_model=DownloadStatusResponse,
    summary="获取下载状态",
    description="获取下载任务的详细状态"
)
def get_download_status(
    task_id: int,
    download_service: DownloadService = Depends(get_download_service)
):
    """获取下载状态"""
    status = download_service.get_download_status(task_id)
    if not status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"下载任务ID {task_id} 不存在"
        )
    return DownloadStatusResponse(**status)


@router.post(
    "/{task_id}/sync",
    response_model=DownloadTaskResponse,
    summary="同步下载状态",
    description="同步下载器状态到本地"
)
def sync_download_status(
    task_id: int,
    download_service: DownloadService = Depends(get_download_service)
):
    """同步下载状态"""
    task = download_service.sync_download_status(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"下载任务ID {task_id} 不存在"
        )
    return DownloadTaskResponse.model_validate(task)


@router.delete(
    "/{task_id}",
    response_model=MessageResponse,
    summary="删除下载任务",
    description="删除下载任务记录"
)
def delete_download_task(
    task_id: int,
    download_service: DownloadService = Depends(get_download_service)
):
    """删除下载任务"""
    success = download_service.delete_download_task(task_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"下载任务ID {task_id} 不存在"
        )
    return MessageResponse(message=f"下载任务ID {task_id} 已删除")