from typing import List, Dict, Optional
from sqlalchemy.orm import Session

from server.site_parsers.base_site_parser import BaseSiteParser
from server.site_parsers.mikan_parser import MikanParser
from server.utils.config import config
from server.services.anime_service import AnimeService


class SmartParserService:
    """智能解析服务"""
    
    def __init__(self):
        self.parsers: List[BaseSiteParser] = []
        self._register_default_parsers()
    
    def _register_default_parsers(self):
        """注册默认的网站解析器"""
        self.register_site_parser(MikanParser())
    
    def register_site_parser(self, parser: BaseSiteParser):
        """注册新的网站解析器
        
        Args:
            parser: 网站解析器实例
        """
        self.parsers.append(parser)
    
    def get_parser(self, url: str) -> Optional[BaseSiteParser]:
        """根据URL获取对应的解析器
        
        Args:
            url: 要解析的URL
            
        Returns:
            Optional[BaseSiteParser]: 对应的解析器，如果没有则返回None
        """
        for parser in self.parsers:
            if parser.can_parse(url):
                return parser
        return None
    
    def parse_anime(self, url: str) -> List[Dict]:
        """解析动画链接，返回可能的动画信息列表
        
        Args:
            url: 动画页面URL
            
        Returns:
            List[Dict]: 动画信息列表
        """
        parser = self.get_parser(url)
        if not parser:
            raise ValueError(f"不支持的网站: {url}")
        
        return parser.parse_anime(url)
    
    def parse_rss(self, url: str, anime_id: int) -> List[Dict]:
        """解析RSS链接，返回可能的RSS源信息列表
        
        Args:
            url: RSS页面URL
            anime_id: 动画ID
            
        Returns:
            List[Dict]: RSS源信息列表
        """
        parser = self.get_parser(url)
        if not parser:
            raise ValueError(f"不支持的网站: {url}")
        
        return parser.parse_rss(url, anime_id)
    
    def parse_anime_with_rss(
        self,
        url: str,
        auto_add_rss: bool = True,
        anime_index: Optional[int] = None,
        rss_indices: Optional[List[int]] = None,
        db: Optional[Session] = None
    ) -> Dict:
        """解析动画链接并自动解析RSS源（连锁解析），并创建动画记录
        
        Args:
            url: 动画页面URL
            auto_add_rss: 是否自动解析RSS源
            anime_index: 选择的动画索引（当有多个结果时，从1开始）
            rss_indices: 选择的RSS源索引列表（从1开始）
            db: 数据库会话
            
        Returns:
            Dict: 解析结果，包含:
                - anime: 创建的动画对象
                - rss_sources: RSS源列表（可选）
        """
        anime_list = self.parse_anime(url)
        if not anime_list:
            raise ValueError("未能解析到动画信息")
        
        # 选择动画
        if anime_index is not None:
            if anime_index < 1 or anime_index > len(anime_list):
                raise ValueError(f"动画索引 {anime_index} 超出范围 (1-{len(anime_list)})")
            anime_info = anime_list[anime_index - 1]
        else:
            # 默认选择第一个
            anime_info = anime_list[0]
        
        # 创建动画记录
        if db is None:
            raise ValueError("数据库会话不能为空")
        
        anime_service = AnimeService(db)
        anime = anime_service.create_anime(
            title=anime_info.get('title', ''),
            title_en=anime_info.get('title_en'),
            description=anime_info.get('description'),
            cover_url=anime_info.get('cover_url'),
            status=anime_info.get('status', 'ongoing'),
            total_episodes=anime_info.get('total_episodes')
        )
        
        result = {
            'anime': anime,
            'rss_sources': []
        }
        
        # 处理RSS源
        if auto_add_rss and 'rss_sources' in anime_info:
            rss_sources_list = anime_info['rss_sources']
            
            # 选择RSS源
            if rss_indices:
                selected_rss = []
                for idx in rss_indices:
                    if idx < 1 or idx > len(rss_sources_list):
                        raise ValueError(f"RSS源索引 {idx} 超出范围 (1-{len(rss_sources_list)})")
                    selected_rss.append(rss_sources_list[idx - 1])
                rss_sources_to_add = selected_rss
            else:
                rss_sources_to_add = rss_sources_list
            
            # TODO: 添加RSS源到数据库（需要实现RSS服务）
            # 这里暂时返回RSS源信息
            result['rss_sources'] = rss_sources_to_add
        
        return result
    
    def get_supported_sites(self) -> List[str]:
        """获取支持的动画网站列表
        
        Returns:
            List[str]: 支持的网站名称列表
        """
        return [parser.get_site_name() for parser in self.parsers]
    
    def get_site_name_from_url(self, url: str) -> str:
        """根据URL获取网站名称
        
        Args:
            url: 动画页面URL
            
        Returns:
            str: 网站名称
        """
        parser = self.get_parser(url)
        if parser:
            return parser.get_site_name()
        return "Unknown"


# 全局智能解析服务实例
smart_parser_service = SmartParserService()