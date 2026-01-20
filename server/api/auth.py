"""
API认证模块
提供API密钥认证的依赖函数
"""
from typing import Optional
from fastapi import Header, HTTPException, status, Depends
from sqlalchemy.orm import Session

from server.database.session import get_db
from server.services.api_key_service import APIKeyService


async def verify_api_key(
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    db: Session = Depends(get_db)
) -> str:
    """验证API密钥的依赖函数
    
    Args:
        x_api_key: 从请求头中获取的API密钥
        db: 数据库会话
        
    Returns:
        验证通过的API密钥字符串
        
    Raises:
        HTTPException: 如果API密钥无效或缺失
    """
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key is missing. Please provide X-API-Key header.",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    # 创建 APIKeyService 实例用于验证
    api_key_service = APIKeyService(db)
    api_key = api_key_service.validate_api_key(x_api_key)
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    return x_api_key