"""
API请求和响应的Pydantic模型
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


# ========== 动画相关模型 ==========

class AnimeBase(BaseModel):
    """动画基础模型"""
    title: str = Field(..., description="动画标题", min_length=1, max_length=255)
    title_en: Optional[str] = Field(None, description="英文标题", max_length=255)
    description: Optional[str] = Field(None, description="描述")
    cover_url: Optional[str] = Field(None, description="封面URL", max_length=500)
    status: str = Field(default='ongoing', description="状态 (ongoing, completed, etc.)")
    total_episodes: Optional[int] = Field(None, description="总集数", ge=0)


class AnimeCreate(AnimeBase):
    """创建动画请求模型"""
    pass


class AnimeUpdate(BaseModel):
    """更新动画请求模型"""
    title: Optional[str] = Field(None, description="动画标题", min_length=1, max_length=255)
    title_en: Optional[str] = Field(None, description="英文标题", max_length=255)
    description: Optional[str] = Field(None, description="描述")
    cover_url: Optional[str] = Field(None, description="封面URL", max_length=500)
    status: Optional[str] = Field(None, description="状态 (ongoing, completed, etc.)")
    total_episodes: Optional[int] = Field(None, description="总集数", ge=0)


class AnimeResponse(AnimeBase):
    """动画响应模型"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime
    updated_at: datetime


class AnimeListResponse(BaseModel):
    """动画列表响应模型"""
    total: int
    items: List[AnimeResponse]
    skip: int
    limit: int


# ========== 智能解析相关模型 ==========

class SmartParseAnimeRequest(BaseModel):
    """智能解析动画请求模型"""
    url: str = Field(..., description="动画网站链接")


class SmartParseAnimeResult(BaseModel):
    """智能解析动画结果模型"""
    title: str = Field(..., description="动画标题")
    title_en: Optional[str] = Field(None, description="英文标题")
    description: Optional[str] = Field(None, description="描述")
    cover_url: Optional[str] = Field(None, description="封面URL")
    status: str = Field(default='ongoing', description="状态")
    total_episodes: Optional[int] = Field(None, description="总集数")
    rss_sources: Optional[List[Dict[str, Any]]] = Field(
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
    anime_index: Optional[int] = Field(None, description="选择的动画索引（当有多个结果时）")
    rss_indices: Optional[List[int]] = Field(
        default_factory=list,
        description="选择的RSS源索引列表（用于连锁解析RSS时）"
    )


class SmartAddAnimeResponse(BaseModel):
    """智能添加动画响应模型"""
    anime: AnimeResponse
    rss_sources: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="添加的RSS源信息"
    )


# ========== 通用响应模型 ==========

class MessageResponse(BaseModel):
    """通用消息响应模型"""
    message: str
    success: bool = True


class ErrorResponse(BaseModel):
    """错误响应模型"""
    error: str
    detail: Optional[str] = None
    success: bool = False


# ========== RSS源相关模型 ==========

class RSSSourceBase(BaseModel):
    """RSS源基础模型"""
    name: str = Field(..., description="RSS源名称", min_length=1, max_length=255)
    url: str = Field(..., description="RSS订阅链接", min_length=1, max_length=500)
    quality: Optional[str] = Field(None, description="画质 (1080p, 720p, etc.)", max_length=50)
    is_active: bool = Field(default=True, description="是否激活")
    auto_download: bool = Field(default=False, description="是否自动下载")


class RSSSourceCreate(RSSSourceBase):
    """创建RSS源请求模型"""
    anime_id: int = Field(..., description="动画ID")


class RSSSourceUpdate(BaseModel):
    """更新RSS源请求模型"""
    name: Optional[str] = Field(None, description="RSS源名称", min_length=1, max_length=255)
    url: Optional[str] = Field(None, description="RSS订阅链接", min_length=1, max_length=500)
    quality: Optional[str] = Field(None, description="画质 (1080p, 720p, etc.)", max_length=50)
    is_active: Optional[bool] = Field(None, description="是否激活")
    auto_download: Optional[bool] = Field(None, description="是否自动下载")


class RSSSourceResponse(RSSSourceBase):
    """RSS源响应模型"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    anime_id: int
    last_checked_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class RSSSourceListResponse(BaseModel):
    """RSS源列表响应模型"""
    total: int
    items: List[RSSSourceResponse]