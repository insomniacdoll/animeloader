#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的Download命令测试
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.test_utils import TestEnvironment
from client.api.client import APIClient
from client.commands.download_commands import DownloadCommands
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
        download_commands = DownloadCommands(api_client, console, {})
        
        # 创建动画、RSS源、链接和下载器
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
        
        link_id = link_response['id']
        
        downloader_response = api_client.post('/api/downloaders', json_data={
            'name': 'Mock下载器',
            'downloader_type': 'mock',
            'config': '{}',
            'is_default': True
        })
        
        if 'error' in downloader_response:
            print(f"Failed to create downloader: {downloader_response['error']}")
            return 1
        
        downloader_id = downloader_response['id']
        
        # 创建下载任务
        download_response = api_client.post('/api/downloads', json_data={
            'link_id': link_id,
            'rss_source_id': rss_id,
            'downloader_id': downloader_id
        })
        
        if 'error' in download_response:
            print(f"Failed to create download task: {download_response['error']}")
            return 1
        
        # 测试列出下载任务
        download_commands.list('')
        
        # 测试显示下载状态
        task_id = download_response['id']
        download_commands.status(f'--id {task_id}')
        
        print("\n[成功] Download命令测试通过")
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
