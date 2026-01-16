from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple


class BaseDownloader(ABC):
    @abstractmethod
    def connect(self, config: Dict[str, Any]) -> bool:
        """连接到下载器"""
        pass

    @abstractmethod
    def disconnect(self) -> bool:
        """断开连接"""
        pass

    @abstractmethod
    def add_task(self, url: str, options: Dict[str, Any]) -> str:
        """添加下载任务，返回任务ID"""
        pass

    @abstractmethod
    def remove_task(self, task_id: str) -> bool:
        """移除下载任务"""
        pass

    @abstractmethod
    def pause_task(self, task_id: str) -> bool:
        """暂停下载任务"""
        pass

    @abstractmethod
    def resume_task(self, task_id: str) -> bool:
        """恢复下载任务"""
        pass

    @abstractmethod
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """获取任务状态"""
        pass

    @abstractmethod
    def get_global_status(self) -> Dict[str, Any]:
        """获取下载器全局状态"""
        pass

    @abstractmethod
    def validate_config(self, config: Dict[str, Any]) -> Tuple[bool, str]:
        """验证配置是否正确，返回(是否有效, 错误信息)"""
        pass