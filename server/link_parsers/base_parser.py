from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseParser(ABC):
    @abstractmethod
    def parse(self, url: str) -> Dict[str, Any]:
        """解析链接，返回链接元数据"""
        pass

    @abstractmethod
    def validate(self, url: str) -> bool:
        """验证链接格式是否正确"""
        pass

    @abstractmethod
    def get_download_command(self, url: str, save_path: str) -> str:
        """获取下载命令"""
        pass