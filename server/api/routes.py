"""
API路由模块
定义所有REST API端点
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from server.database import get_db
from server.services.anime_service import AnimeService
from server.services.smart_parser_service import SmartParserService
from server.api.schemas import (
    AnimeCreate,
    AnimeUpdate,
    AnimeResponse,
    AnimeListResponse,
    SmartParseAnimeRequest,
    SmartParseAnimeResponse,
    SmartAddAnimeRequest,
    SmartAddAnimeResponse,
    RSSSourceCreate,
    RSSSourceUpdate,
    RSSSourceResponse,
    RSSSourceListResponse,
    MessageResponse,
    ErrorResponse
)
from server.services.rss_service import RSSService


# 创建路由器
router = APIRouter(prefix="/api", tags=["API"])


# ========== 依赖注入 ==========

def get_anime_service(db: Session = Depends(get_db)) -> AnimeService:
    """获取动画服务实例"""
    return AnimeService(db)


def get_smart_parser_service() -> SmartParserService:
    """获取智能解析服务实例"""
    return SmartParserService()


def get_rss_service(db: Session = Depends(get_db)) -> RSSService:
    """获取RSS源服务实例"""
    return RSSService(db)


# ========== 动画相关API ==========

@router.get(
    "/anime",
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
    "/anime/{anime_id}",
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
    "/anime",
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
    "/anime/{anime_id}",
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
    "/anime/{anime_id}",
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


# ========== 智能解析相关API ==========

@router.post(
    "/anime/smart-parse",
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
    "/anime/smart-add",
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
            anime=AnimeResponse.model_validate(result['anime']),
            rss_sources=result.get('rss_sources', [])
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"智能添加失败: {str(e)}"
        )


# ========== RSS源相关API ==========

@router.get(
    "/anime/{anime_id}/rss-sources",
    response_model=RSSSourceListResponse,
    summary="获取动画的所有RSS源",
    description="根据动画ID获取该动画的所有RSS源"
)
def get_anime_rss_sources(
    anime_id: int,
    db: Session = Depends(get_db),
    rss_service: RSSService = Depends(get_rss_service)
):
    """获取动画的所有RSS源"""
    rss_sources = rss_service.get_rss_sources(anime_id)
    return RSSSourceListResponse(
        total=len(rss_sources),
        items=[RSSSourceResponse.model_validate(rss) for rss in rss_sources]
    )


@router.get(
    "/rss-sources/{rss_source_id}",
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
    "/rss-sources",
    response_model=RSSSourceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建RSS源",
    description="创建新的RSS源记录"
)
def create_rss_source(
    rss_data: RSSSourceCreate,
    rss_service: RSSService = Depends(get_rss_service)
):
    """创建RSS源"""
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
    "/rss-sources/{rss_source_id}",
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
    "/rss-sources/{rss_source_id}",
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


# ========== 智能解析通用API ==========

@router.get(
    "/smart-parser/sites",
    response_model=MessageResponse,
    summary="获取支持的网站列表",
    description="获取智能解析支持的动画网站列表"
)
def get_supported_sites(
    smart_parser_service: SmartParserService = Depends(get_smart_parser_service)
):
    """获取支持的网站列表"""
    sites = smart_parser_service.get_supported_sites()
    return MessageResponse(
        message=f"支持的网站: {', '.join(sites)}",
        success=True
    )


@router.post(
    "/smart-parser/parse-anime",
    response_model=SmartParseAnimeResponse,
    summary="解析动画链接",
    description="解析动画网站链接，返回可能的动画信息列表"
)
def parse_anime_link(
    request: SmartParseAnimeRequest,
    smart_parser_service: SmartParserService = Depends(get_smart_parser_service)
):
    """解析动画链接"""
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


# ========== 健康检查 ==========

@router.get(
    "/health",
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