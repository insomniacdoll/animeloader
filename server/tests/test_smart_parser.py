#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试蜜柑计划解析器
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from server.site_parsers.mikan_parser import MikanParser


def test_mikan_parser():
    """测试蜜柑计划解析器"""
    print("=" * 60)
    print("测试蜜柑计划解析器")
    print("=" * 60)
    
    parser = MikanParser()
    test_url = "https://mikanani.me/Home/Bangumi/3824"
    
    print(f"\n测试URL: {test_url}")
    print(f"网站名称: {parser.get_site_name()}")
    print(f"是否支持解析: {parser.can_parse(test_url)}")
    
    if not parser.can_parse(test_url):
        print("[错误] 不支持该URL")
        return False
    
    print("\n开始解析动画信息...")
    try:
        anime_list = parser.parse_anime(test_url)
        
        if not anime_list:
            print("[错误] 未能解析到动画信息")
            return False
        
        print(f"\n成功解析到 {len(anime_list)} 个动画:")
        
        for idx, anime in enumerate(anime_list, 1):
            print(f"\n动画 {idx}:")
            print(f"  标题: {anime.get('title', '')}")
            print(f"  英文标题: {anime.get('title_en', '')}")
            print(f"  描述: {anime.get('description', '')}")
            print(f"  封面URL: {anime.get('cover_url', '')}")
            print(f"  状态: {anime.get('status', '')}")
            print(f"  总集数: {anime.get('total_episodes', 0)}")
            
            rss_sources = anime.get('rss_sources', [])
            if rss_sources:
                print(f"  RSS源 ({len(rss_sources)} 个):")
                for rss in rss_sources:
                    print(f"    - 名称: {rss.get('name', '')}")
                    print(f"      URL: {rss.get('url', '')}")
                    print(f"      画质: {rss.get('quality', '')}")
                    print(f"      自动下载: {rss.get('auto_download', False)}")
        
        print("\n" + "=" * 60)
        print("[成功] 解析测试完成")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"[错误] 解析失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = test_mikan_parser()
    sys.exit(0 if success else 1)