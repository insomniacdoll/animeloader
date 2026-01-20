"""
下载器服务模块
提供下载器管理相关的业务逻辑
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
import json

from server.models.downloader import Downloader


class DownloaderService:
    """下载器服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def add_downloader(
        self,
        name: str,
        downloader_type: str = "mock",
        config: Optional[Dict[str, Any]] = None,
        is_default: bool = False,
        max_concurrent_tasks: int = 3
    ) -> Downloader:
        """添加下载器"""
        # 如果设置为默认，先将其他下载器的默认状态设为 False
        if is_default:
            self.db.query(Downloader).filter(Downloader.is_default == True).update(
                {"is_default": False}
            )
        
        downloader = Downloader(
            name=name,
            downloader_type=downloader_type,
            config=json.dumps(config) if config else "{}",
            is_active=True,
            is_default=is_default,
            max_concurrent_tasks=max_concurrent_tasks
        )
        self.db.add(downloader)
        self.db.commit()
        self.db.refresh(downloader)
        return downloader
    
    def get_downloader(self, downloader_id: int) -> Optional[Downloader]:
        """获取单个下载器"""
        return self.db.query(Downloader).filter(Downloader.id == downloader_id).first()
    
    def get_downloaders(
        self,
        is_active: Optional[bool] = None,
        downloader_type: Optional[str] = None
    ) -> List[Downloader]:
        """获取所有下载器，支持过滤"""
        query = self.db.query(Downloader)
        
        if is_active is not None:
            query = query.filter(Downloader.is_active == is_active)
        
        if downloader_type is not None:
            query = query.filter(Downloader.downloader_type == downloader_type)
        
        return query.all()
    
    def get_default_downloader(self) -> Optional[Downloader]:
        """获取默认下载器"""
        return self.db.query(Downloader).filter(Downloader.is_default == True).first()
    
    def get_downloader_by_type(self, downloader_type: str) -> Optional[Downloader]:
        """根据类型获取下载器"""
        return self.db.query(Downloader).filter(
            Downloader.downloader_type == downloader_type
        ).first()
    
    def update_downloader(
        self,
        downloader_id: int,
        name: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        is_active: Optional[bool] = None,
        is_default: Optional[bool] = None,
        max_concurrent_tasks: Optional[int] = None
    ) -> Optional[Downloader]:
        """更新下载器配置"""
        downloader = self.get_downloader(downloader_id)
        if not downloader:
            return None
        
        # 如果设置为默认，先将其他下载器的默认状态设为 False
        if is_default is True:
            self.db.query(Downloader).filter(
                and_(
                    Downloader.is_default == True,
                    Downloader.id != downloader_id
                )
            ).update({"is_default": False})
        
        if name is not None:
            downloader.name = name
        if config is not None:
            downloader.config = json.dumps(config)
        if is_active is not None:
            downloader.is_active = is_active
        if is_default is not None:
            downloader.is_default = is_default
        if max_concurrent_tasks is not None:
            downloader.max_concurrent_tasks = max_concurrent_tasks
        
        self.db.commit()
        self.db.refresh(downloader)
        return downloader
    
    def set_default_downloader(self, downloader_id: int) -> Optional[Downloader]:
        """设置默认下载器"""
        # 先将所有下载器的默认状态设为 False
        self.db.query(Downloader).filter(Downloader.is_default == True).update(
            {"is_default": False}
        )
        
        downloader = self.get_downloader(downloader_id)
        if not downloader:
            return None
        
        downloader.is_default = True
        self.db.commit()
        self.db.refresh(downloader)
        return downloader
    
    def delete_downloader(self, downloader_id: int) -> bool:
        """删除下载器"""
        downloader = self.get_downloader(downloader_id)
        if not downloader:
            return False
        
        self.db.delete(downloader)
        self.db.commit()
        return True
    
    def test_downloader(self, downloader_id: int) -> Dict[str, Any]:
        """测试下载器连接（Mock实现）"""
        downloader = self.get_downloader(downloader_id)
        if not downloader:
            return {
                "success": False,
                "message": f"下载器 ID {downloader_id} 不存在"
            }
        
        # Mock 实现：总是返回成功
        return {
            "success": True,
            "message": f"下载器 '{downloader.name}' 连接测试成功",
            "downloader_type": downloader.downloader_type
        }
    
    def get_downloader_status(self, downloader_id: int) -> Dict[str, Any]:
        """获取下载器状态（当前任务数等）"""
        downloader = self.get_downloader(downloader_id)
        if not downloader:
            return {
                "success": False,
                "message": f"下载器 ID {downloader_id} 不存在"
            }
        
        # Mock 实现：返回模拟状态
        return {
            "success": True,
            "downloader_id": downloader_id,
            "name": downloader.name,
            "type": downloader.downloader_type,
            "is_active": downloader.is_active,
            "max_concurrent_tasks": downloader.max_concurrent_tasks,
            "active_tasks": 0,  # Mock 值
            "total_tasks": 0     # Mock 值
        }
    
    def get_supported_downloader_types(self) -> List[str]:
        """获取支持的下载器类型列表"""
        return ["mock", "aria2", "pikpak"]
    
    def validate_downloader_config(self, downloader_type: str, config: Dict[str, Any]) -> tuple[bool, str]:
        """验证下载器配置"""
        # Mock 实现：总是返回有效
        return True, "配置有效"