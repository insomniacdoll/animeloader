"""
RSS源相关API路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from server.database import get_db
from server.services.rss_service import RSSService
from server.services.scheduler_service import SchedulerService
from server.api.schemas import (
    RSSSourceCreate,
    RSSSourceUpdate,
    RSSSourceResponse,
    RSSSourceListResponse,
    MessageResponse
)
from server.api.auth import verify_api_key


# 在路由器级别添加认证依赖
router = APIRouter(
    prefix="/rss-sources",
    tags=["RSS源"],
    dependencies=[Depends(verify_api_key)]
)


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


def get_rss_service(
    db: Session = Depends(get_db),
    scheduler_service: SchedulerService = Depends(get_scheduler_service)
) -> RSSService:
    """获取RSS源服务实例"""
    return RSSService(db, scheduler_service)


@router.get(
    "",
    response_model=RSSSourceListResponse,
    summary="获取所有RSS源",
    description="获取所有RSS源列表，支持按动画ID过滤"
)
def get_rss_sources(
    anime_id: int | None = None,
    rss_service: RSSService = Depends(get_rss_service)
):
    """获取所有RSS源"""
    if anime_id is not None:
        rss_sources = rss_service.get_rss_sources(anime_id)
    else:
        # 获取所有RSS源
        rss_sources = rss_service.get_all_rss_sources()
    
    return RSSSourceListResponse(
        total=len(rss_sources),
        items=[RSSSourceResponse.model_validate(rss) for rss in rss_sources]
    )


@router.get(
    "/{rss_source_id}",
    response_model=RSSSourceResponse,
    summary="获取单个RSS源",
    description="根据ID获取单个RSS源的详细信息"
)
def get_rss_source(
    rss_source_id: int,
    rss_service: RSSService = Depends(get_rss_service)
):
    """获取单个RSS源"""
    rss_source = rss_service.get_rss_source(rss_source_id)
    if not rss_source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"RSS源ID {rss_source_id} 不存在"
        )
    return RSSSourceResponse.model_validate(rss_source)


@router.post(
    "",
    response_model=RSSSourceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建RSS源",
    description="创建新的RSS源记录，如果同一动画下已存在相同URL的RSS源则返回已存在的记录"
)
def create_rss_source(
    rss_data: RSSSourceCreate,
    rss_service: RSSService = Depends(get_rss_service)
):
    """创建RSS源，自动防止重复添加"""
    rss_source = rss_service.create_rss_source(
        anime_id=rss_data.anime_id,
        name=rss_data.name,
        url=rss_data.url,
        quality=rss_data.quality,
        is_active=rss_data.is_active,
        auto_download=rss_data.auto_download
    )
    return RSSSourceResponse.model_validate(rss_source)


@router.put(
    "/{rss_source_id}",
    response_model=RSSSourceResponse,
    summary="更新RSS源",
    description="更新RSS源信息"
)
def update_rss_source(
    rss_source_id: int,
    rss_data: RSSSourceUpdate,
    rss_service: RSSService = Depends(get_rss_service)
):
    """更新RSS源"""
    rss_source = rss_service.update_rss_source(
        rss_source_id=rss_source_id,
        name=rss_data.name,
        url=rss_data.url,
        quality=rss_data.quality,
        is_active=rss_data.is_active,
        auto_download=rss_data.auto_download
    )
    if not rss_source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"RSS源ID {rss_source_id} 不存在"
        )
    return RSSSourceResponse.model_validate(rss_source)


@router.delete(
    "/{rss_source_id}",
    response_model=MessageResponse,
    summary="删除RSS源",
    description="删除RSS源记录"
)
def delete_rss_source(
    rss_source_id: int,
    rss_service: RSSService = Depends(get_rss_service)
):
    """删除RSS源"""
    success = rss_service.delete_rss_source(rss_source_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"RSS源ID {rss_source_id} 不存在"
        )
    return MessageResponse(message=f"RSS源ID {rss_source_id} 已删除")