from typing import List, Dict
import requests
from bs4 import BeautifulSoup
from .base_site_parser import BaseSiteParser


class MikanParser(BaseSiteParser):
    """蜜柑计划网站解析器"""
    
    def __init__(self):
        self.site_name = "蜜柑计划"
    
    def can_parse(self, url: str) -> bool:
        """判断是否可以解析该URL"""
        return 'mikanani.me' in url or 'mikanani.org' in url
    
    def parse_anime(self, url: str) -> List[Dict]:
        """解析动画信息，返回可能的动画列表
        
        Args:
            url: 动画页面URL
            
        Returns:
            List[Dict]: 动画信息列表
        """
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 解析动画信息
            anime_info = {
                'title': '',
                'title_en': '',
                'description': '',
                'cover_url': '',
                'status': 'ongoing',
                'total_episodes': 0,
                'rss_sources': []
            }
            
            # 提取标题
            title_element = soup.find('h3', class_='bangumi-title')
            if title_element:
                anime_info['title'] = title_element.get_text(strip=True)
            
            # 提取英文标题
            title_en_element = soup.find('p', class_='bangumi-info')
            if title_en_element:
                anime_info['title_en'] = title_en_element.get_text(strip=True)
            
            # 提取封面
            cover_element = soup.find('img', class_='bangumi-cover')
            if cover_element:
                anime_info['cover_url'] = cover_element.get('src', '')
            
            # 提取描述
            desc_element = soup.find('div', class_='bangumi-description')
            if desc_element:
                anime_info['description'] = desc_element.get_text(strip=True)
            
            # 提取RSS源
            rss_elements = soup.find_all('a', class_='mikan-rss')
            for rss_element in rss_elements:
                quality = rss_element.get_text(strip=True)
                rss_url = rss_element.get('href', '')
                if rss_url and not rss_url.startswith('http'):
                    rss_url = f"https://mikanani.me{rss_url}"
                
                anime_info['rss_sources'].append({
                    'name': f'{self.site_name} {quality}',
                    'url': rss_url,
                    'quality': quality,
                    'auto_download': True
                })
            
            return [anime_info]
            
        except Exception as e:
            print(f"解析蜜柑计划动画信息失败: {e}")
            return []
    
    def parse_rss(self, url: str, anime_id: int) -> List[Dict]:
        """解析RSS源信息，返回可能的RSS源列表
        
        Args:
            url: RSS页面URL
            anime_id: 动画ID
            
        Returns:
            List[Dict]: RSS源信息列表
        """
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            rss_sources = []
            
            # 提取RSS源信息
            rss_element = soup.find('a', class_='rss-link')
            if rss_element:
                quality = rss_element.get_text(strip=True)
                rss_url = rss_element.get('href', '')
                if rss_url and not rss_url.startswith('http'):
                    rss_url = f"https://mikanani.me{rss_url}"
                
                rss_sources.append({
                    'name': f'{self.site_name} {quality}',
                    'url': rss_url,
                    'quality': quality,
                    'auto_download': True
                })
            
            return rss_sources
            
        except Exception as e:
            print(f"解析蜜柑计划RSS源信息失败: {e}")
            return []
    
    def get_site_name(self) -> str:
        """获取网站名称"""
        return self.site_name