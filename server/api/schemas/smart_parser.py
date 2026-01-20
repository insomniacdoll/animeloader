"""
智能解析相关模型
"""
from typing import List, Dict, Any, TYPE_CHECKING
from pydantic import BaseModel, Field


class SmartParseAnimeRequest(BaseModel):
    """智能解析动画请求模型"""
    url: str = Field(..., description="动画网站链接")


class SmartParseAnimeResult(BaseModel):
    """智能解析动画结果模型"""
    title: str = Field(..., description="动画标题")
    title_en: str | None = Field(None, description="英文标题")
    description: str | None = Field(None, description="描述")
    cover_url: str | None = Field(None, description="封面URL")
    status: str = Field(default='ongoing', description="状态")
    total_episodes: int | None = Field(None, description="总集数")
    rss_sources: List[Dict[str, Any]] | None = Field(
        default_factory=list,
        description="解析到的RSS源信息（可选）"
    )


class SmartParseAnimeResponse(BaseModel):
    """智能解析动画响应模型"""
    site_name: str = Field(..., description="网站名称")
    results: List[SmartParseAnimeResult] = Field(..., description="解析结果列表")


class SmartAddAnimeRequest(BaseModel):
    """智能添加动画请求模型"""
    url: str = Field(..., description="动画网站链接")
    auto_add_rss: bool = Field(default=True, description="是否自动解析并添加RSS源")
    anime_index: int | None = Field(None, description="选择的动画索引（当有多个结果时）")
    rss_indices: List[int] | None = Field(
        default_factory=list,
        description="选择的RSS源索引列表（用于连锁解析RSS时）"
    )


# 使用 TYPE_CHECKING 避免运行时循环导入
if TYPE_CHECKING:
    from .anime import AnimeResponse


class SmartAddAnimeResponse(BaseModel):
    """智能添加动画响应模型"""
    anime: Any  # 运行时使用 Any，类型检查时使用 AnimeResponse
    rss_sources: List[Dict[str, Any]] | None = Field(
        default_factory=list,
        description="添加的RSS源信息"
    )