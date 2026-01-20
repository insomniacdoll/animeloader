"""
调度服务相关模型
"""
from typing import Dict, Any
from pydantic import BaseModel, Field


class SchedulerJobCreate(BaseModel):
    """创建调度任务请求模型"""
    rss_source_id: int = Field(..., description="RSS源ID")
    interval: int = Field(default=3600, description="检查间隔（秒）", ge=60)
    auto_download: bool = Field(default=False, description="是否自动下载新链接")


class SchedulerJobResponse(BaseModel):
    """调度任务响应模型"""
    job_id: str
    name: str
    next_run_time: str | None
    info: Dict[str, Any]


class SchedulerJobsResponse(BaseModel):
    """调度任务列表响应模型"""
    jobs: Dict[str, Dict[str, Any]]


class RSSCheckResponse(BaseModel):
    """RSS检查响应模型"""
    success: bool
    message: str
    rss_source_id: int
    new_links_count: int
    new_links: list[Dict[str, Any]]
    checked_at: str