"""
蜜柑计划RSS解析器
解析蜜柑计划网站的RSS源
"""
import feedparser
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
from urllib.parse import urljoin, urlparse

from .base_rss_parser import BaseRSSParser


class MikanRSSParser(BaseRSSParser):
    """蜜柑计划RSS解析器"""
    
    def __init__(self):
        self.site_name = "蜜柑计划"
        self.base_url = "https://mikanani.me"
    
    def can_parse(self, url: str) -> bool:
        """判断是否可以解析该RSS源URL"""
        return 'mikanani.me' in url or 'mikanani.org' in url
    
    def parse_rss(self, rss_url: str, existing_urls: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        解析蜜柑计划RSS源

        Args:
            rss_url: RSS源URL
            existing_urls: 已存在的链接URL列表

        Returns:
            解析结果
        """
        try:
            # 解析RSS
            feed = feedparser.parse(rss_url)
            
            if feed.bozo:
                return {
                    'success': False,
                    'error': f'RSS解析失败: {feed.bozo_exception}'
                }
            
            # 提取链接
            links = []
            for entry in feed.entries:
                link_info = self._parse_entry(entry, rss_url)
                if link_info:
                    links.append(link_info)
            
            result = {
                'success': True,
                'feed_title': feed.feed.get('title', ''),
                'feed_description': feed.feed.get('description', ''),
                'feed_link': feed.feed.get('link', ''),
                'total_entries': len(feed.entries),
                'links': links,
                'new_links': [],
                'new_links_count': 0
            }
            
            # 如果提供了已存在的链接，过滤出新链接
            if existing_urls:
                existing_set = set(existing_urls)
                new_links = [link for link in links if link['url'] not in existing_set]
                result['new_links'] = new_links
                result['new_links_count'] = len(new_links)
            else:
                result['new_links'] = links
                result['new_links_count'] = len(links)
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': f'RSS解析异常: {str(e)}'
            }
    
    def _parse_entry(self, entry: Any, rss_url: str) -> Optional[Dict[str, Any]]:
        """
        解析单个RSS条目

        Args:
            entry: RSS条目
            rss_url: RSS源URL

        Returns:
            链接信息字典
        """
        # 获取标题
        title = entry.get('title', '')
        
        # 获取发布日期
        publish_date = None
        if 'published_parsed' in entry:
            publish_date = datetime(*entry.published_parsed[:6])
        elif 'updated_parsed' in entry:
            publish_date = datetime(*entry.updated_parsed[:6])
        
        # 获取描述
        description = entry.get('description', '') or entry.get('summary', '')
        
        # 从标题中提取集数
        episode_number = self.extract_episode_number(title)
        
        # 从标题中提取集标题
        episode_title = self.extract_episode_title(title)
        
        # 从entry中提取下载链接
        download_links = self._extract_download_links(entry)
        
        if not download_links:
            return None
        
        # 返回第一个有效的下载链接
        for link_info in download_links:
            link_info.update({
                'episode_number': episode_number,
                'episode_title': episode_title,
                'publish_date': publish_date,
                'entry_title': title,
                'entry_description': description
            })
            return link_info
        
        return None
    
    def _extract_download_links(self, entry: Any) -> List[Dict[str, Any]]:
        """
        从entry中提取下载链接

        Args:
            entry: RSS条目

        Returns:
            下载链接列表
        """
        links = []
        
        # 检查links字段 - 处理磁力链接
        if hasattr(entry, 'links'):
            for link in entry.links:
                url = link.get('href', '')
                
                # 处理磁力链接
                if url.startswith('magnet:'):
                    # 简单验证磁力链接格式
                    if 'xt=urn:btih:' in url:
                        links.append({
                            'link_type': 'magnet',
                            'url': url,
                            'file_size': 0,
                            'filename': entry.get('title', ''),
                            'meta_data': f'magnet_link:{url}'
                        })
        
        # 检查enclosures（蜜柑计划的种子文件在这里）
        # 如果找到种子文件，直接存储为torrent类型，由上层服务决定如何处理
        if hasattr(entry, 'enclosures'):
            for enclosure in entry.enclosures:
                url = enclosure.get('href', '')
                enclosure_type = enclosure.get('type', '')
                length = enclosure.get('length', 0)
                
                # 处理种子文件，保持为torrent类型
                if enclosure_type == 'application/x-bittorrent' or url.endswith('.torrent'):
                    try:
                        file_size = int(length) if length else 0
                        filename = self._extract_filename_from_url(url) or entry.get('title', '')
                        links.append({
                            'link_type': 'torrent',  # 保持为torrent类型
                            'url': url,
                            'file_size': file_size,
                            'filename': filename,
                            'meta_data': f'torrent_file:{url}'
                        })
                    except (ValueError, TypeError):
                        pass
        
        return links
    
    def _extract_filename_from_url(self, url: str) -> str:
        """
        从URL中提取文件名

        Args:
            url: URL

        Returns:
            文件名
        """
        parsed = urlparse(url)
        path = parsed.path
        filename = path.split('/')[-1]
        return filename
    
    def get_site_name(self) -> str:
        """获取网站名称"""
        return self.site_name