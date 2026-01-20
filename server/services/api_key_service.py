"""
API密钥服务模块
提供API密钥验证相关的业务逻辑
"""
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from server.models.api_key import APIKey


class APIKeyService:
    """API密钥服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def validate_api_key(self, key: str) -> Optional[APIKey]:
        """验证API密钥是否有效
        
        Args:
            key: API密钥字符串
            
        Returns:
            如果验证成功返回APIKey对象，否则返回None
        """
        # 查询激活且未过期的密钥
        api_key = self.db.query(APIKey).filter(
            and_(
                APIKey.key == key,
                APIKey.is_active == True,
                or_(
                    APIKey.expires_at.is_(None),
                    APIKey.expires_at > datetime.utcnow()
                )
            )
        ).first()
        
        if api_key:
            # 更新最后使用时间
            api_key.last_used_at = datetime.utcnow()
            self.db.commit()
        
        return api_key
    
    def get_default_api_key(self) -> Optional[APIKey]:
        """获取默认API密钥
        
        Returns:
            默认API密钥对象，如果不存在则返回None
        """
        return self.db.query(APIKey).filter(APIKey.is_default == True).first()
    
    def create_default_key(self) -> APIKey:
        """创建默认API密钥
        
        Returns:
            新创建的默认API密钥对象
        """
        import uuid
        
        default_key = APIKey(
            name="Default API Key",
            key=str(uuid.uuid4()),
            description="系统默认API密钥，用于客户端访问",
            is_active=True,
            is_default=True
        )
        self.db.add(default_key)
        self.db.commit()
        self.db.refresh(default_key)
        return default_key
    
    def initialize_default_key(self) -> APIKey:
        """初始化默认API密钥
        
        如果默认密钥不存在则创建，否则返回现有的默认密钥
        
        Returns:
            默认API密钥对象
        """
        default_key = self.get_default_api_key()
        if not default_key:
            default_key = self.create_default_key()
        return default_key