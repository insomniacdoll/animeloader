from typing import List, Dict, Optional
from server.site_parsers.base_site_parser import BaseSiteParser
from server.site_parsers.mikan_parser import MikanParser
from server.utils.config import config


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
    
    def parse_anime_with_rss(self, url: str, auto_add_rss: bool = True) -> Dict:
        """解析动画链接并自动解析RSS源（连锁解析）
        
        Args:
            url: 动画页面URL
            auto_add_rss: 是否自动解析RSS源
            
        Returns:
            Dict: 解析结果，包含:
                - anime: 动画信息
                - rss_sources: RSS源列表（可选）
        """
        anime_list = self.parse_anime(url)
        if not anime_list:
            raise ValueError("未能解析到动画信息")
        
        # 取第一个动画信息
        anime_info = anime_list[0]
        
        result = {
            'anime': anime_info,
            'rss_sources': []
        }
        
        # 如果有RSS源信息且启用自动解析
        if auto_add_rss and 'rss_sources' in anime_info:
            result['rss_sources'] = anime_info['rss_sources']
        
        return result
    
    def get_supported_sites(self) -> List[str]:
        """获取支持的动画网站列表
        
        Returns:
            List[str]: 支持的网站名称列表
        """
        return [parser.get_site_name() for parser in self.parsers]


# 全局智能解析服务实例
smart_parser_service = SmartParserService()