#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的Link命令测试
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.test_utils import TestEnvironment
from client.api.client import APIClient
from client.commands.link_commands import LinkCommands
from rich.console import Console

def main():
    env = TestEnvironment()
    try:
        env.setup()
        
        if not env.start_server():
            print("Failed to start server")
            return 1
        
        # 获取API密钥
        from server.utils import init_config
        from server.database import get_db, get_engine
        from server.services.api_key_service import APIKeyService
        from server.models import Base
        
        init_config(env.get_config_path())
        
        engine = get_engine()
        Base.metadata.create_all(bind=engine)
        
        SessionLocal = next(get_db())
        api_key_service = APIKeyService(SessionLocal)
        default_key = api_key_service.get_default_api_key()
        SessionLocal.close()
        
        if not default_key:
            print("Failed to get API key")
            return 1
        
        # 创建API客户端
        api_client = APIClient(base_url=env.get_server_url(), api_key=default_key.key)
        console = Console()
        link_commands = LinkCommands(api_client, console, {})
        
        # 创建动画和RSS源
        anime_response = api_client.post('/api/anime', json_data={
            'title': '测试动画',
            'status': 'ongoing'
        })
        
        if 'error' in anime_response:
            print(f"Failed to create anime: {anime_response['error']}")
            return 1
        
        anime_id = anime_response['id']
        
        rss_response = api_client.post('/api/rss-sources', json_data={
            'anime_id': anime_id,
            'name': '测试RSS源',
            'url': 'https://example.com/rss',
            'quality': '1080p',
            'auto_download': True
        })
        
        if 'error' in rss_response:
            print(f"Failed to create RSS source: {rss_response['error']}")
            return 1
        
        rss_id = rss_response['id']
        
        # 创建链接
        link_response = api_client.post('/api/links', json_data={
            'rss_source_id': rss_id,
            'episode_number': 1,
            'episode_title': '第1集',
            'link_type': 'magnet',
            'url': 'magnet:?xt=urn:btih:test',
            'file_size': 1024000,
            'publish_date': '2026-01-21T00:00:00'
        })
        
        if 'error' in link_response:
            print(f"Failed to create link: {link_response['error']}")
            return 1
        
        # 测试列出链接
        link_commands.list('')
        
        # 测试显示链接详情
        link_id = link_response['id']
        link_commands.show(f'--id {link_id}')
        
        print("\n[成功] Link命令测试通过")
        return 0
    except Exception as e:
        print(f"[失败] 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        env.teardown()

if __name__ == '__main__':
    sys.exit(main())
