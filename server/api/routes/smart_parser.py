"""
智能解析相关API路由
"""
from fastapi import APIRouter, Depends, HTTPException, status

from server.services.smart_parser_service import SmartParserService
from server.api.schemas.smart_parser import (
    SmartParseAnimeRequest,
    SmartParseAnimeResponse
)
from server.api.schemas.common import MessageResponse
from server.api.auth import verify_api_key


router = APIRouter(prefix="/smart-parser", tags=["智能解析"])


def get_smart_parser_service() -> SmartParserService:
    """获取智能解析服务实例"""
    return SmartParserService()


@router.get(
    "/sites",
    response_model=MessageResponse,
    summary="获取支持的网站列表",
    description="获取智能解析支持的动画网站列表"
)
def get_supported_sites(
    api_key: str = Depends(verify_api_key),
    smart_parser_service: SmartParserService = Depends(get_smart_parser_service)
):
    """获取支持的网站列表"""
    sites = smart_parser_service.get_supported_sites()
    return MessageResponse(
        message=f"支持的网站: {', '.join(sites)}",
        success=True
    )


@router.post(
    "/parse-anime",
    response_model=SmartParseAnimeResponse,
    summary="解析动画链接",
    description="解析动画网站链接，返回可能的动画信息列表"
)
def parse_anime_link(
    request: SmartParseAnimeRequest,
    api_key: str = Depends(verify_api_key),
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