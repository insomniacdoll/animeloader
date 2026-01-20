"""
下载器相关API路由
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from server.database import get_db
from server.services.downloader_service import DownloaderService
from server.api.schemas import (
    DownloaderCreate,
    DownloaderUpdate,
    DownloaderResponse,
    DownloaderListResponse,
    DownloaderTestResponse,
    DownloaderStatusResponse,
    MessageResponse
)
from server.api.auth import verify_api_key


router = APIRouter(prefix="/downloaders", tags=["下载器"])


def get_downloader_service(db: Session = Depends(get_db)) -> DownloaderService:
    """获取下载器服务实例"""
    return DownloaderService(db)


@router.get(
    "",
    response_model=DownloaderListResponse,
    summary="获取所有下载器",
    description="获取所有下载器列表"
)
def get_downloaders(
    api_key: str = Depends(verify_api_key),
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
    "/{downloader_id}",
    response_model=DownloaderResponse,
    summary="获取单个下载器",
    description="根据ID获取单个下载器的详细信息"
)
def get_downloader(
    downloader_id: int,
    api_key: str = Depends(verify_api_key),
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
    "/default",
    response_model=DownloaderResponse,
    summary="获取默认下载器",
    description="获取默认下载器"
)
def get_default_downloader(
    api_key: str = Depends(verify_api_key),
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
    "/types",
    response_model=MessageResponse,
    summary="获取支持的下载器类型",
    description="获取支持的下载器类型列表"
)
def get_downloader_types(
    api_key: str = Depends(verify_api_key),
    downloader_service: DownloaderService = Depends(get_downloader_service)
):
    """获取支持的下载器类型"""
    types = downloader_service.get_supported_downloader_types()
    return MessageResponse(
        message=f"支持的下载器类型: {', '.join(types)}",
        success=True
    )


@router.post(
    "",
    response_model=DownloaderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建下载器",
    description="创建新的下载器记录"
)
def create_downloader(
    downloader_data: DownloaderCreate,
    api_key: str = Depends(verify_api_key),
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
    "/{downloader_id}",
    response_model=DownloaderResponse,
    summary="更新下载器",
    description="更新下载器配置"
)
def update_downloader(
    downloader_id: int,
    downloader_data: DownloaderUpdate,
    api_key: str = Depends(verify_api_key),
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
    "/{downloader_id}/set-default",
    response_model=DownloaderResponse,
    summary="设置为默认下载器",
    description="设置指定下载器为默认下载器"
)
def set_default_downloader(
    downloader_id: int,
    api_key: str = Depends(verify_api_key),
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
    "/{downloader_id}/test",
    response_model=DownloaderTestResponse,
    summary="测试下载器连接",
    description="测试下载器连接是否正常"
)
def test_downloader(
    downloader_id: int,
    api_key: str = Depends(verify_api_key),
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
    "/{downloader_id}/status",
    response_model=DownloaderStatusResponse,
    summary="获取下载器状态",
    description="获取下载器的当前状态"
)
def get_downloader_status(
    downloader_id: int,
    api_key: str = Depends(verify_api_key),
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
    "/{downloader_id}",
    response_model=MessageResponse,
    summary="删除下载器",
    description="删除下载器记录"
)
def delete_downloader(
    downloader_id: int,
    api_key: str = Depends(verify_api_key),
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