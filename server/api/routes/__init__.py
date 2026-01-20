"""
API路由模块
"""
from fastapi import APIRouter
from .anime import router as anime_router
from .anime_extra import router as anime_extra_router
from .rss import router as rss_router
from .rss_extra import router as rss_extra_router
from .link import router as link_router
from .link_extra import router as link_extra_router
from .downloader import router as downloader_router
from .download import router as download_router
from .scheduler import router as scheduler_router
from .smart_parser import router as smart_parser_router
from .health import router as health_router


def create_api_router() -> APIRouter:
    """创建API路由器"""
    router = APIRouter(prefix="/api", tags=["API"])
    
    # 注册各个子路由
    router.include_router(anime_router)
    router.include_router(anime_extra_router)
    router.include_router(rss_router)
    router.include_router(rss_extra_router)
    router.include_router(link_router)
    router.include_router(link_extra_router)
    router.include_router(downloader_router)
    router.include_router(download_router)
    router.include_router(scheduler_router)
    router.include_router(smart_parser_router)
    router.include_router(health_router)
    
    return router


__all__ = ["create_api_router"]