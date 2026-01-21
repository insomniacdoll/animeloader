"""
RSS解析器基类
定义RSS解析器的通用接口
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime


class BaseRSSParser(ABC):
    """RSS解析器基类"""
    
    @abstractmethod
    def can_parse(self, url: str) -> bool:
        """
        判断是否可以解析该RSS源URL

        Args:
            url: RSS源URL

        Returns:
            bool: 是否可以解析
        """
        pass
    
    @abstractmethod
    def parse_rss(self, rss_url: str, existing_urls: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        解析RSS源

        Args:
            rss_url: RSS源URL
            existing_urls: 已存在的链接URL列表，用于过滤新链接

        Returns:
            Dict[str, Any]: 解析结果，包含：
                - success: 是否成功
                - feed_title: Feed标题
                - feed_description: Feed描述
                - feed_link: Feed链接
                - total_entries: 总条目数
                - links: 所有链接列表
                - new_links: 新链接列表（如果提供了existing_urls）
                - new_links_count: 新链接数量
                - error: 错误信息（如果失败）
        """
        pass
    
    @abstractmethod
    def get_site_name(self) -> str:
        """
        获取网站名称

        Returns:
            str: 网站名称
        """
        pass
    
    def extract_episode_number(self, title: str) -> Optional[int]:
        """
        从标题中提取集数（通用方法）

        Args:
            title: 标题

        Returns:
            集数，提取失败返回None
        """
        import re

        # 尝试匹配 "第X集" 格式
        match = re.search(r'第(\d+)集', title)
        if match:
            return int(match.group(1))

        # 尝试匹配 "EP.X" 或 "EPX" 格式
        match = re.search(r'EP\.?(\d+)', title, re.IGNORECASE)
        if match:
            return int(match.group(1))

        # 尝试匹配 "[X]" 格式
        match = re.search(r'\[(\d+)\]', title)
        if match:
            return int(match.group(1))

        # 尝试匹配 "【X】" 格式（全角方括号）
        match = re.search(r'【(\d+)】', title)
        if match:
            return int(match.group(1))

        # 尝试匹配 " - X" 或 " X " 格式
        match = re.search(r'[\s\-_](\d+)(?:[\s\-_]|$)', title)
        if match:
            num = int(match.group(1))
            # 只返回合理的集数（1-999）
            if 1 <= num <= 999:
                return num

        return None
    
    def extract_episode_title(self, title: str) -> str:
        """
        从标题中提取集标题（通用方法）

        Args:
            title: 标题

        Returns:
            集标题
        """
        import re

        # 移除常见的标签和格式
        # 移除文件扩展名
        title = re.sub(r'\.(mkv|mp4|avi|rmvb|wmv|flv|ts|m2ts)$', '', title, flags=re.IGNORECASE)

        # 移除方括号内的内容（通常包含字幕组、分辨率等信息）
        title = re.sub(r'\[[^\]]+\]', '', title)

        # 移除圆括号内的内容
        title = re.sub(r'\([^)]+\)', '', title)

        # 移除集数标记
        title = re.sub(r'第\d+集', '', title)
        title = re.sub(r'EP\.?\d+', '', title, flags=re.IGNORECASE)

        # 清理多余空格和符号
        title = re.sub(r'[\s\-_]+', ' ', title)
        title = title.strip()

        return title