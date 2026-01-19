#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试智能添加功能
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from server.utils import init_config
from server.database import init_database, get_session_local
from server.services.smart_parser_service import smart_parser_service
from server.services.anime_service import AnimeService
from server.services.rss_service import RSSService


def test_smart_add():
    """测试智能添加功能"""
    print("=" * 60)
    print("测试智能添加功能")
    print("=" * 60)
    
    # 初始化配置
    print("\n初始化配置...")
    config = init_config()
    
    # 初始化数据库
    print("\n初始化数据库...")
    init_database()
    
    # 获取数据库会话
    SessionLocal = get_session_local()
    db = SessionLocal()
    
    try:
        test_url = "https://mikanani.me/Home/Bangumi/3824"
        print(f"\n测试URL: {test_url}")
        
        # 测试智能解析
        print("\n1. 测试智能解析...")
        anime_list = smart_parser_service.parse_anime(test_url)
        
        if not anime_list:
            print("[错误] 未能解析到动画信息")
            return False
        
        print(f"✓ 成功解析到 {len(anime_list)} 个动画")
        print(f"  - 标题: {anime_list[0].get('title', '')}")
        
        # 测试智能添加（不带RSS）
        print("\n2. 测试智能添加（不带RSS）...")
        result = smart_parser_service.parse_anime_with_rss(
            url=test_url,
            auto_add_rss=False,
            db=db
        )
        
        anime = result['anime']
        print(f"✓ 动画添加成功")
        print(f"  - ID: {anime.id}")
        print(f"  - 标题: {anime.title}")
        print(f"  - 英文标题: {anime.title_en}")
        
        # 测试添加RSS源
        print("\n3. 测试添加RSS源...")
        rss_service = RSSService(db)
        
        rss_source = rss_service.create_rss_source(
            anime_id=anime.id,
            name="蜜柑计划 默认",
            url="https://mikanani.me/RSS/Bangumi?bangumiId=3824",
            quality="default",
            auto_download=True
        )
        
        print(f"✓ RSS源添加成功")
        print(f"  - ID: {rss_source.id}")
        print(f"  - 名称: {rss_source.name}")
        print(f"  - URL: {rss_source.url}")
        
        # 测试查询动画
        print("\n4. 测试查询动画...")
        anime_service = AnimeService(db)
        
        queried_anime = anime_service.get_anime(anime.id)
        print(f"✓ 动画查询成功")
        print(f"  - ID: {queried_anime.id}")
        print(f"  - 标题: {queried_anime.title}")
        
        # 测试查询RSS源
        print("\n5. 测试查询RSS源...")
        rss_sources = rss_service.get_rss_sources(anime.id)
        print(f"✓ RSS源查询成功")
        print(f"  - 数量: {len(rss_sources)}")
        for rss in rss_sources:
            print(f"    - {rss.name} (ID: {rss.id})")
        
        # 测试获取动画列表
        print("\n6. 测试获取动画列表...")
        animes = anime_service.get_animes()
        print(f"✓ 动画列表获取成功")
        print(f"  - 总数: {len(animes)}")
        for a in animes:
            print(f"    - {a.title} (ID: {a.id})")
        
        print("\n" + "=" * 60)
        print("[成功] 测试完成")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"[错误] 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


if __name__ == '__main__':
    success = test_smart_add()
    sys.exit(0 if success else 1)