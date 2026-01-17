from abc import ABC, abstractmethod
from typing import List, Dict


class BaseSiteParser(ABC):
    """网站解析器基类"""
    
    @abstractmethod
    def can_parse(self, url: str) -> bool:
        """判断是否可以解析该URL
        
        Args:
            url: 要解析的URL
            
        Returns:
            bool: 是否可以解析
        """
        pass
    
    @abstractmethod
    def parse_anime(self, url: str) -> List[Dict]:
        """解析动画信息，返回可能的动画列表
        
        Args:
            url: 动画页面URL
            
        Returns:
            List[Dict]: 动画信息列表，每个元素包含：
                - title: 动画标题
                - title_en: 英文标题
                - description: 描述
                - cover_url: 封面URL
                - status: 状态 (ongoing, completed, etc.)
                - total_episodes: 总集数
                - rss_sources: 可选，RSS源列表
        """
        pass
    
    @abstractmethod
    def parse_rss(self, url: str, anime_id: int) -> List[Dict]:
        """解析RSS源信息，返回可能的RSS源列表
        
        Args:
            url: RSS页面URL
            anime_id: 动画ID
            
        Returns:
            List[Dict]: RSS源信息列表，每个元素包含：
                - name: RSS源名称
                - url: RSS订阅链接
                - quality: 画质
                - auto_download: 是否自动下载
        """
        pass
    
    @abstractmethod
    def get_site_name(self) -> str:
        """获取网站名称
        
        Returns:
            str: 网站名称
        """
        pass