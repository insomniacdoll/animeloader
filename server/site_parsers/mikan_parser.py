from typing import List, Dict
import requests
from bs4 import BeautifulSoup
from .base_site_parser import BaseSiteParser


class MikanParser(BaseSiteParser):
    """蜜柑计划网站解析器"""
    
    def __init__(self):
        self.site_name = "蜜柑计划"
        self.base_url = "https://mikanani.me"
    
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
            
            # 提取所有RSS源（在修改DOM之前）
            # 首先添加默认RSS（没有subgroupid的）
            rss_links = soup.find_all('a', class_='mikan-rss')
            default_rss = None
            for rss_link in rss_links:
                rss_url = rss_link.get('href', '')
                # 检查是否是默认RSS（不包含subgroupid参数）
                if rss_url and 'subgroupid=' not in rss_url:
                    if not rss_url.startswith('http'):
                        rss_url = f"{self.base_url}{rss_url}"
                    default_rss = rss_url
                    break
            
            if default_rss:
                anime_info['rss_sources'].append({
                    'name': f'{self.site_name} 默认',
                    'url': default_rss,
                    'quality': 'default',
                    'auto_download': True
                })
            
            # 提取标题
            title_element = soup.find('p', class_='bangumi-title')
            if title_element:
                # 移除RSS链接图标
                rss_link = title_element.find('a', class_='mikan-rss')
                if rss_link:
                    rss_link.decompose()
                anime_info['title'] = title_element.get_text(strip=True)
            
            # 提取封面
            cover_element = soup.find('div', class_='bangumi-poster')
            if cover_element:
                style = cover_element.get('style', '')
                # 从background-image中提取URL
                if 'background-image' in style:
                    start = style.find('url(') + 4
                    end = style.find(')', start)
                    cover_url = style[start:end].strip("'\"")
                    if cover_url and not cover_url.startswith('http'):
                        cover_url = f"{self.base_url}{cover_url}"
                    anime_info['cover_url'] = cover_url
            
            # 提取描述和其他信息
            info_elements = soup.find_all('p', class_='bangumi-info')
            description_parts = []
            for info_element in info_elements:
                text = info_element.get_text(strip=True)
                if text and not text.startswith('官方网站') and not text.startswith('Bangumi'):
                    if '放送日期' in text or '放送开始' in text:
                        description_parts.append(text)
            
            anime_info['description'] = '\n'.join(description_parts)
            
            # 提取字幕组RSS源
            import re
            subgroup_links = soup.find_all('a', class_=re.compile(r'subgroup-\d+'))
            for link in subgroup_links:
                classes = link.get('class', [])
                subgroup_id = None
                for cls in classes:
                    if cls.startswith('subgroup-') and cls != 'subgroup-name':
                        subgroup_id = cls.replace('subgroup-', '')
                        break
                
                if subgroup_id:
                    name = link.get_text(strip=True)
                    rss_url = f"{self.base_url}/RSS/Bangumi?bangumiId={url.split('/')[-1]}&subgroupid={subgroup_id}"
                    
                    anime_info['rss_sources'].append({
                        'name': f'{name}',
                        'url': rss_url,
                        'quality': 'default',
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
            
            # 蜜柑计划的RSS链接本身就是RSS源
            rss_sources = []
            
            rss_sources.append({
                'name': f'{self.site_name} RSS',
                'url': url,
                'quality': 'default',
                'auto_download': True
            })
            
            return rss_sources
            
        except Exception as e:
            print(f"解析蜜柑计划RSS源信息失败: {e}")
            return []
    
    def get_site_name(self) -> str:
        """获取网站名称"""
        return self.site_name