"""
RSS源相关扩展API路由（链接和检查）
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from server.database import get_db
from server.services.link_service import LinkService
from server.services.scheduler_service import SchedulerService
from server.api.schemas import (
    LinkListResponse,
    LinkResponse,
    MessageResponse,
    RSSCheckResponse
)
from server.api.auth import verify_api_key


# 在路由器级别添加认证依赖
router = APIRouter(
    prefix="/rss-sources",
    tags=["RSS源扩展"],
    dependencies=[Depends(verify_api_key)]
)


def get_link_service(db: Session = Depends(get_db)) -> LinkService:
    """获取链接服务实例"""
    return LinkService(db)


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
    "/{rss_source_id}/links",
    response_model=LinkListResponse,
    summary="获取RSS源的所有链接",
    description="根据RSS源ID获取该RSS源的所有链接"
)
def get_rss_source_links(
    rss_source_id: int,
    is_downloaded: Optional[bool] = Query(None, description="是否已下载"),
    link_type: Optional[str] = Query(None, description="链接类型"),
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回的记录数"),
    link_service: LinkService = Depends(get_link_service)
):
    """获取RSS源的所有链接"""
    total = link_service.count_links(
        rss_source_id=rss_source_id,
        is_downloaded=is_downloaded,
        link_type=link_type
    )
    links = link_service.get_links(
        rss_source_id=rss_source_id,
        is_downloaded=is_downloaded,
        link_type=link_type,
        skip=skip,
        limit=limit
    )
    
    return LinkListResponse(
        total=total,
        items=[LinkResponse.model_validate(link) for link in links],
        skip=skip,
        limit=limit
    )


@router.post(
    "/{rss_source_id}/check",
    response_model=RSSCheckResponse,
    summary="手动检查RSS源新链接",
    description="手动检查RSS源的新链接"
)
def check_rss_source(
    rss_source_id: int,
    auto_download: bool = Query(False, description="是否自动下载新链接"),
    scheduler_service: SchedulerService = Depends(get_scheduler_service)
):
    """手动检查RSS源新链接"""
    result = scheduler_service.check_rss_source(rss_source_id, auto_download=auto_download)
    return RSSCheckResponse(**result)