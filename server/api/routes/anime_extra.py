"""
动画相关扩展API路由（RSS源）
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from server.database import get_db
from server.services.rss_service import RSSService
from server.api.schemas import (
    RSSSourceListResponse,
    RSSSourceResponse
)
from server.api.auth import verify_api_key


# 在路由器级别添加认证依赖
router = APIRouter(
    prefix="/anime",
    tags=["动画扩展"],
    dependencies=[Depends(verify_api_key)]
)


def get_rss_service(db: Session = Depends(get_db)) -> RSSService:
    """获取RSS源服务实例"""
    return RSSService(db)


@router.get(
    "/{anime_id}/rss-sources",
    response_model=RSSSourceListResponse,
    summary="获取动画的所有RSS源",
    description="根据动画ID获取该动画的所有RSS源"
)
def get_anime_rss_sources(
    anime_id: int,
    rss_service: RSSService = Depends(get_rss_service)
):
    """获取动画的所有RSS源"""
    rss_sources = rss_service.get_rss_sources(anime_id)
    return RSSSourceListResponse(
        total=len(rss_sources),
        items=[RSSSourceResponse.model_validate(rss) for rss in rss_sources]
    )