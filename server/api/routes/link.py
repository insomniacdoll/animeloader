"""
链接相关API路由
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from server.database import get_db
from server.services.link_service import LinkService
from server.api.schemas import (
    LinkCreate,
    LinkUpdate,
    LinkResponse,
    LinkListResponse,
    MessageResponse
)
from server.api.auth import verify_api_key


# 在路由器级别添加认证依赖
router = APIRouter(
    prefix="/links",
    tags=["链接"],
    dependencies=[Depends(verify_api_key)]
)


def get_link_service(db: Session = Depends(get_db)) -> LinkService:
    """获取链接服务实例"""
    return LinkService(db)


@router.get(
    "",
    response_model=LinkListResponse,
    summary="获取链接列表",
    description="获取所有链接，支持过滤"
)
def get_links(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回的记录数"),
    link_type: Optional[str] = Query(None, description="链接类型"),
    is_downloaded: Optional[bool] = Query(None, description="是否已下载"),
    link_service: LinkService = Depends(get_link_service)
):
    """获取链接列表"""
    total = link_service.count_links(
        link_type=link_type,
        is_downloaded=is_downloaded
    )
    links = link_service.get_all_links(
        skip=skip,
        limit=limit,
        link_type=link_type,
        is_downloaded=is_downloaded
    )
    
    return LinkListResponse(
        total=total,
        items=[LinkResponse.model_validate(link) for link in links],
        skip=skip,
        limit=limit
    )


@router.get(
    "/{link_id}",
    response_model=LinkResponse,
    summary="获取单个链接",
    description="根据ID获取单个链接的详细信息"
)
def get_link(
    link_id: int,
    link_service: LinkService = Depends(get_link_service)
):
    """获取单个链接"""
    link = link_service.get_link(link_id)
    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"链接ID {link_id} 不存在"
        )
    return LinkResponse.model_validate(link)


@router.post(
    "",
    response_model=LinkResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建链接",
    description="创建新的链接记录"
)
def create_link(
    link_data: LinkCreate,
    link_service: LinkService = Depends(get_link_service)
):
    """创建链接"""
    link = link_service.add_link(
        rss_source_id=link_data.rss_source_id,
        episode_number=link_data.episode_number,
        episode_title=link_data.episode_title,
        link_type=link_data.link_type,
        url=link_data.url,
        file_size=link_data.file_size
    )
    return LinkResponse.model_validate(link)


@router.put(
    "/{link_id}",
    response_model=LinkResponse,
    summary="更新链接",
    description="更新链接状态"
)
def update_link(
    link_id: int,
    link_data: LinkUpdate,
    link_service: LinkService = Depends(get_link_service)
):
    """更新链接"""
    link = link_service.update_link_status(
        link_id=link_id,
        is_available=link_data.is_available,
        is_downloaded=link_data.is_downloaded
    )
    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"链接ID {link_id} 不存在"
        )
    return LinkResponse.model_validate(link)


@router.post(
    "/{link_id}/mark-downloaded",
    response_model=LinkResponse,
    summary="标记为已下载",
    description="标记链接为已下载"
)
def mark_link_as_downloaded(
    link_id: int,
    link_service: LinkService = Depends(get_link_service)
):
    """标记链接为已下载"""
    link = link_service.mark_as_downloaded(link_id)
    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"链接ID {link_id} 不存在"
        )
    return LinkResponse.model_validate(link)


@router.delete(
    "/{link_id}",
    response_model=MessageResponse,
    summary="删除链接",
    description="删除链接记录"
)
def delete_link(
    link_id: int,
    link_service: LinkService = Depends(get_link_service)
):
    """删除链接"""
    success = link_service.delete_link(link_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"链接ID {link_id} 不存在"
        )
    return MessageResponse(message=f"链接ID {link_id} 已删除")