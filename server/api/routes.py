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
from server.services.link_service import LinkService
from server.services.downloader_service import DownloaderService
from server.services.download_service import DownloadService
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
    ErrorResponse,
    LinkCreate,
    LinkUpdate,
    LinkResponse,
    LinkListResponse,
    DownloaderCreate,
    DownloaderUpdate,
    DownloaderResponse,
    DownloaderListResponse,
    DownloaderTestResponse,
    DownloaderStatusResponse,
    DownloadTaskCreate,
    DownloadTaskResponse,
    DownloadTaskListResponse,
    DownloadStatusResponse,
    SchedulerJobCreate,
    SchedulerJobResponse,
    SchedulerJobsResponse,
    RSSCheckResponse
)
from server.services.link_service import LinkService
from server.services.downloader_service import DownloaderService
from server.services.download_service import DownloadService


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


def get_link_service(db: Session = Depends(get_db)) -> LinkService:
    """获取链接服务实例"""
    return LinkService(db)


def get_downloader_service(db: Session = Depends(get_db)) -> DownloaderService:
    """获取下载器服务实例"""
    return DownloaderService(db)


def get_download_service(db: Session = Depends(get_db)) -> DownloadService:
    """获取下载服务实例"""
    return DownloadService(db)


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


# ========== 链接相关API ==========

@router.get(
    "/rss-sources/{rss_source_id}/links",
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


@router.get(
    "/links/{link_id}",
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


@router.get(
    "/links",
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


@router.post(
    "/links",
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
    "/links/{link_id}",
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
    "/links/{link_id}/mark-downloaded",
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
    "/links/{link_id}",
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


# ========== 下载器相关API ==========

@router.get(
    "/downloaders",
    response_model=DownloaderListResponse,
    summary="获取所有下载器",
    description="获取所有下载器列表"
)
def get_downloaders(
    is_active: Optional[bool] = Query(None, description="是否激活"),
    downloader_type: Optional[str] = Query(None, description="下载器类型"),
    downloader_service: DownloaderService = Depends(get_downloader_service)
):
    """获取所有下载器"""
    downloaders = downloader_service.get_downloaders(
        is_active=is_active,
        downloader_type=downloader_type
    )
    return DownloaderListResponse(
        total=len(downloaders),
        items=[DownloaderResponse.model_validate(d) for d in downloaders]
    )


@router.get(
    "/downloaders/{downloader_id}",
    response_model=DownloaderResponse,
    summary="获取单个下载器",
    description="根据ID获取单个下载器的详细信息"
)
def get_downloader(
    downloader_id: int,
    downloader_service: DownloaderService = Depends(get_downloader_service)
):
    """获取单个下载器"""
    downloader = downloader_service.get_downloader(downloader_id)
    if not downloader:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"下载器ID {downloader_id} 不存在"
        )
    return DownloaderResponse.model_validate(downloader)


@router.get(
    "/downloaders/default",
    response_model=DownloaderResponse,
    summary="获取默认下载器",
    description="获取默认下载器"
)
def get_default_downloader(
    downloader_service: DownloaderService = Depends(get_downloader_service)
):
    """获取默认下载器"""
    downloader = downloader_service.get_default_downloader()
    if not downloader:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="默认下载器不存在"
        )
    return DownloaderResponse.model_validate(downloader)


@router.get(
    "/downloaders/types",
    response_model=MessageResponse,
    summary="获取支持的下载器类型",
    description="获取支持的下载器类型列表"
)
def get_downloader_types(
    downloader_service: DownloaderService = Depends(get_downloader_service)
):
    """获取支持的下载器类型"""
    types = downloader_service.get_supported_downloader_types()
    return MessageResponse(
        message=f"支持的下载器类型: {', '.join(types)}",
        success=True
    )


@router.post(
    "/downloaders",
    response_model=DownloaderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建下载器",
    description="创建新的下载器记录"
)
def create_downloader(
    downloader_data: DownloaderCreate,
    downloader_service: DownloaderService = Depends(get_downloader_service)
):
    """创建下载器"""
    downloader = downloader_service.add_downloader(
        name=downloader_data.name,
        downloader_type=downloader_data.downloader_type,
        config=downloader_data.config,
        is_default=downloader_data.is_default,
        max_concurrent_tasks=downloader_data.max_concurrent_tasks
    )
    return DownloaderResponse.model_validate(downloader)


@router.put(
    "/downloaders/{downloader_id}",
    response_model=DownloaderResponse,
    summary="更新下载器",
    description="更新下载器配置"
)
def update_downloader(
    downloader_id: int,
    downloader_data: DownloaderUpdate,
    downloader_service: DownloaderService = Depends(get_downloader_service)
):
    """更新下载器"""
    downloader = downloader_service.update_downloader(
        downloader_id=downloader_id,
        name=downloader_data.name,
        config=downloader_data.config,
        is_active=downloader_data.is_active,
        is_default=downloader_data.is_default,
        max_concurrent_tasks=downloader_data.max_concurrent_tasks
    )
    if not downloader:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"下载器ID {downloader_id} 不存在"
        )
    return DownloaderResponse.model_validate(downloader)


@router.post(
    "/downloaders/{downloader_id}/set-default",
    response_model=DownloaderResponse,
    summary="设置为默认下载器",
    description="设置指定下载器为默认下载器"
)
def set_default_downloader(
    downloader_id: int,
    downloader_service: DownloaderService = Depends(get_downloader_service)
):
    """设置为默认下载器"""
    downloader = downloader_service.set_default_downloader(downloader_id)
    if not downloader:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"下载器ID {downloader_id} 不存在"
        )
    return DownloaderResponse.model_validate(downloader)


@router.post(
    "/downloaders/{downloader_id}/test",
    response_model=DownloaderTestResponse,
    summary="测试下载器连接",
    description="测试下载器连接是否正常"
)
def test_downloader(
    downloader_id: int,
    downloader_service: DownloaderService = Depends(get_downloader_service)
):
    """测试下载器连接"""
    result = downloader_service.test_downloader(downloader_id)
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )
    return DownloaderTestResponse(**result)


@router.get(
    "/downloaders/{downloader_id}/status",
    response_model=DownloaderStatusResponse,
    summary="获取下载器状态",
    description="获取下载器的当前状态"
)
def get_downloader_status(
    downloader_id: int,
    downloader_service: DownloaderService = Depends(get_downloader_service)
):
    """获取下载器状态"""
    result = downloader_service.get_downloader_status(downloader_id)
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result["message"]
        )
    return DownloaderStatusResponse(**result)


@router.delete(
    "/downloaders/{downloader_id}",
    response_model=MessageResponse,
    summary="删除下载器",
    description="删除下载器记录"
)
def delete_downloader(
    downloader_id: int,
    downloader_service: DownloaderService = Depends(get_downloader_service)
):
    """删除下载器"""
    success = downloader_service.delete_downloader(downloader_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"下载器ID {downloader_id} 不存在"
        )
    return MessageResponse(message=f"下载器ID {downloader_id} 已删除")


# ========== 下载任务相关API ==========

@router.get(
    "/downloads",
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
    "/downloads/active",
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
    "/downloads/{task_id}",
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


@router.get(
    "/links/{link_id}/downloads",
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


@router.post(
    "/downloads",
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
    "/downloads/{task_id}/start",
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
    "/downloads/{task_id}/pause",
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
    "/downloads/{task_id}/resume",
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
    "/downloads/{task_id}/cancel",
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
    "/downloads/{task_id}/status",
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
    "/downloads/{task_id}/sync",
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
    "/downloads/{task_id}",
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


# ========== 调度服务相关API ==========

@router.get(
    "/scheduler/jobs",
    response_model=SchedulerJobsResponse,
    summary="获取所有调度任务",
    description="获取所有调度任务列表"
)
def get_scheduler_jobs():
    """获取所有调度任务"""
    # 这里需要从全局获取 scheduler_service 实例
    # 暂时返回空列表
    return SchedulerJobsResponse(jobs={})


@router.post(
    "/scheduler/jobs",
    response_model=MessageResponse,
    summary="创建调度任务",
    description="创建新的调度任务"
)
def create_scheduler_job(
    job_data: SchedulerJobCreate
):
    """创建调度任务"""
    # 这里需要从全局获取 scheduler_service 实例
    # 暂时返回成功
    return MessageResponse(
        message=f"调度任务创建成功: rss_check_{job_data.rss_source_id}",
        success=True
    )


@router.delete(
    "/scheduler/jobs/{job_id}",
    response_model=MessageResponse,
    summary="删除调度任务",
    description="删除调度任务"
)
def delete_scheduler_job(
    job_id: str
):
    """删除调度任务"""
    # 这里需要从全局获取 scheduler_service 实例
    # 暂时返回成功
    return MessageResponse(
        message=f"调度任务 {job_id} 已删除",
        success=True
    )


@router.post(
    "/rss-sources/{rss_source_id}/check",
    response_model=RSSCheckResponse,
    summary="手动检查RSS源新链接",
    description="手动检查RSS源的新链接"
)
def check_rss_source(
    rss_source_id: int,
    auto_download: bool = Query(False, description="是否自动下载新链接")
):
    """手动检查RSS源新链接"""
    # 这里需要从全局获取 scheduler_service 实例
    # 暂时返回模拟结果
    return RSSCheckResponse(
        success=True,
        message=f"检查完成，发现 0 个新链接",
        rss_source_id=rss_source_id,
        new_links_count=0,
        new_links=[],
        checked_at=datetime.utcnow().isoformat()
    )

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