"""
动画相关API路由
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from server.database import get_db
from server.services.anime_service import AnimeService
from server.api.schemas import (
    AnimeCreate,
    AnimeUpdate,
    AnimeResponse,
    AnimeListResponse,
    MessageResponse
)
from server.api.schemas.smart_parser import SmartAddAnimeResponse
from server.services.smart_parser_service import SmartParserService
from server.api.schemas.smart_parser import (
    SmartParseAnimeRequest,
    SmartParseAnimeResponse,
    SmartAddAnimeRequest
)
from server.api.schemas.anime import AnimeResponse as AnimeResponseSchema
from server.api.auth import verify_api_key


# 在路由器级别添加认证依赖（类似Java Spring的AOP切面）
router = APIRouter(
    prefix="/anime",
    tags=["动画"],
    dependencies=[Depends(verify_api_key)]  # 所有路由自动应用认证
)


def get_anime_service(db: Session = Depends(get_db)) -> AnimeService:
    """获取动画服务实例"""
    return AnimeService(db)


def get_smart_parser_service() -> SmartParserService:
    """获取智能解析服务实例"""
    return SmartParserService()


@router.get(
    "",
    response_model=AnimeListResponse,
    summary="搜索动画",
    description="获取动画列表，支持搜索和过滤"
)
def get_animes(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回的记录数"),
    search: Optional[str] = Query(None, description="搜索关键词（标题、英文标题、描述）"),
    status: Optional[str] = Query(None, description="状态过滤 (ongoing, completed, etc.)"),
    anime_service: AnimeService = Depends(get_anime_service)
):
    """获取动画列表"""
    total = anime_service.count_animes(search=search, status=status)
    animes = anime_service.get_animes(skip=skip, limit=limit, search=search, status=status)
    
    return AnimeListResponse(
        total=total,
        items=[AnimeResponse.model_validate(anime) for anime in animes],
        skip=skip,
        limit=limit
    )


@router.get(
    "/{anime_id}",
    response_model=AnimeResponse,
    summary="获取动画详情",
    description="根据ID获取单个动画的详细信息"
)
def get_anime(
    anime_id: int,
    anime_service: AnimeService = Depends(get_anime_service)
):
    """获取单个动画详情"""
    anime = anime_service.get_anime(anime_id)
    if not anime:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"动画ID {anime_id} 不存在"
        )
    return AnimeResponse.model_validate(anime)


@router.post(
    "",
    response_model=AnimeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建动画",
    description="创建新的动画记录"
)
def create_anime(
    anime_data: AnimeCreate,
    anime_service: AnimeService = Depends(get_anime_service)
):
    """创建动画"""
    anime = anime_service.create_anime(
        title=anime_data.title,
        title_en=anime_data.title_en,
        description=anime_data.description,
        cover_url=anime_data.cover_url,
        status=anime_data.status,
        total_episodes=anime_data.total_episodes
    )
    return AnimeResponse.model_validate(anime)


@router.put(
    "/{anime_id}",
    response_model=AnimeResponse,
    summary="更新动画",
    description="更新动画信息"
)
def update_anime(
    anime_id: int,
    anime_data: AnimeUpdate,
    anime_service: AnimeService = Depends(get_anime_service)
):
    """更新动画"""
    anime = anime_service.update_anime(
        anime_id=anime_id,
        title=anime_data.title,
        title_en=anime_data.title_en,
        description=anime_data.description,
        cover_url=anime_data.cover_url,
        status=anime_data.status,
        total_episodes=anime_data.total_episodes
    )
    if not anime:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"动画ID {anime_id} 不存在"
        )
    return AnimeResponse.model_validate(anime)


@router.delete(
    "/{anime_id}",
    response_model=MessageResponse,
    summary="删除动画",
    description="删除动画记录"
)
def delete_anime(
    anime_id: int,
    anime_service: AnimeService = Depends(get_anime_service)
):
    """删除动画"""
    success = anime_service.delete_anime(anime_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"动画ID {anime_id} 不存在"
        )
    return MessageResponse(message=f"动画ID {anime_id} 已删除")


@router.post(
    "/smart-parse",
    response_model=SmartParseAnimeResponse,
    summary="智能解析动画信息",
    description="从动画网站链接自动解析动画信息"
)
def smart_parse_anime(
    request: SmartParseAnimeRequest,
    smart_parser_service: SmartParserService = Depends(get_smart_parser_service)
):
    """智能解析动画信息"""
    try:
        results = smart_parser_service.parse_anime(request.url)
        site_name = smart_parser_service.get_site_name_from_url(request.url)
        
        return SmartParseAnimeResponse(
            site_name=site_name,
            results=results
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"解析失败: {str(e)}"
        )


@router.post(
    "/smart-add",
    response_model=SmartAddAnimeResponse,
    summary="智能添加动画",
    description="从动画网站链接智能解析并添加动画，支持连锁解析RSS源"
)
def smart_add_anime(
    request: SmartAddAnimeRequest,
    db: Session = Depends(get_db),
    smart_parser_service: SmartParserService = Depends(get_smart_parser_service)
):
    """智能添加动画（支持连锁解析RSS）"""
    try:
        # 调用智能解析服务的智能添加方法
        result = smart_parser_service.parse_anime_with_rss(
            url=request.url,
            auto_add_rss=request.auto_add_rss,
            anime_index=request.anime_index,
            rss_indices=request.rss_indices,
            db=db
        )
        
        return SmartAddAnimeResponse(
            anime=AnimeResponseSchema.model_validate(result['anime']),
            rss_sources=result.get('rss_sources', [])
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"智能添加失败: {str(e)}"
        )