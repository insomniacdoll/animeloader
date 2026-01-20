"""
调度服务相关API路由
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from server.database import get_db
from server.services.scheduler_service import SchedulerService
from server.api.schemas import (
    SchedulerJobCreate,
    SchedulerJobsResponse,
    MessageResponse,
    RSSCheckResponse
)
from server.api.auth import verify_api_key


router = APIRouter(prefix="/scheduler", tags=["调度服务"])


# 全局调度服务实例（需要在应用启动时设置）
_scheduler_service: SchedulerService | None = None


def set_scheduler_service(service: SchedulerService):
    """设置全局调度服务实例"""
    global _scheduler_service
    _scheduler_service = service


def get_scheduler_service() -> SchedulerService:
    """获取调度服务实例"""
    if _scheduler_service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="调度服务未启动"
        )
    return _scheduler_service


@router.get(
    "/jobs",
    response_model=SchedulerJobsResponse,
    summary="获取所有调度任务",
    description="获取所有调度任务列表"
)
def get_scheduler_jobs(
    api_key: str = Depends(verify_api_key),
    scheduler_service: SchedulerService = Depends(get_scheduler_service)
):
    """获取所有调度任务"""
    jobs = scheduler_service.get_jobs()
    return SchedulerJobsResponse(jobs=jobs)


@router.post(
    "/jobs",
    response_model=MessageResponse,
    summary="创建调度任务",
    description="创建新的调度任务"
)
def create_scheduler_job(
    job_data: SchedulerJobCreate,
    api_key: str = Depends(verify_api_key),
    scheduler_service: SchedulerService = Depends(get_scheduler_service)
):
    """创建调度任务"""
    job_id = scheduler_service.add_check_job(
        rss_source_id=job_data.rss_source_id,
        interval=job_data.interval,
        auto_download=job_data.auto_download
    )
    return MessageResponse(
        message=f"调度任务创建成功: {job_id}",
        success=True
    )


@router.delete(
    "/jobs/{job_id}",
    response_model=MessageResponse,
    summary="删除调度任务",
    description="删除调度任务"
)
def delete_scheduler_job(
    job_id: str,
    api_key: str = Depends(verify_api_key),
    scheduler_service: SchedulerService = Depends(get_scheduler_service)
):
    """删除调度任务"""
    success = scheduler_service.remove_check_job(job_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"调度任务 {job_id} 不存在"
        )
    return MessageResponse(
        message=f"调度任务 {job_id} 已删除",
        success=True
    )


@router.post(
    "/jobs/{job_id}/pause",
    response_model=MessageResponse,
    summary="暂停调度任务",
    description="暂停调度任务"
)
def pause_scheduler_job(
    job_id: str,
    api_key: str = Depends(verify_api_key),
    scheduler_service: SchedulerService = Depends(get_scheduler_service)
):
    """暂停调度任务"""
    success = scheduler_service.pause_job(job_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"调度任务 {job_id} 不存在"
        )
    return MessageResponse(
        message=f"调度任务 {job_id} 已暂停",
        success=True
    )


@router.post(
    "/jobs/{job_id}/resume",
    response_model=MessageResponse,
    summary="恢复调度任务",
    description="恢复调度任务"
)
def resume_scheduler_job(
    job_id: str,
    api_key: str = Depends(verify_api_key),
    scheduler_service: SchedulerService = Depends(get_scheduler_service)
):
    """恢复调度任务"""
    success = scheduler_service.resume_job(job_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"调度任务 {job_id} 不存在"
        )
    return MessageResponse(
        message=f"调度任务 {job_id} 已恢复",
        success=True
    )


@router.post(
    "/start",
    response_model=MessageResponse,
    summary="启动调度器",
    description="启动调度器"
)
def start_scheduler(
    api_key: str = Depends(verify_api_key),
    scheduler_service: SchedulerService = Depends(get_scheduler_service)
):
    """启动调度器"""
    scheduler_service.start_scheduler()
    return MessageResponse(
        message="调度器已启动",
        success=True
    )


@router.post(
    "/stop",
    response_model=MessageResponse,
    summary="停止调度器",
    description="停止调度器"
)
def stop_scheduler(
    api_key: str = Depends(verify_api_key),
    scheduler_service: SchedulerService = Depends(get_scheduler_service)
):
    """停止调度器"""
    scheduler_service.stop_scheduler()
    return MessageResponse(
        message="调度器已停止",
        success=True
    )