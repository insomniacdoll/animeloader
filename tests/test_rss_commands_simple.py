#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的RSS命令测试
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.test_utils import TestEnvironment
from client.api.client import APIClient
from client.commands.rss_commands import RSSCommands
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
        rss_commands = RSSCommands(api_client, console, {})
        
        # 创建动画
        anime_response = api_client.post('/api/anime', json_data={
            'title': '测试动画',
            'status': 'ongoing'
        })
        
        if 'error' in anime_response:
            print(f"Failed to create anime: {anime_response['error']}")
            return 1
        
        anime_id = anime_response['id']
        
        # 测试添加RSS源
        args = f'--anime-id {anime_id} --name "测试RSS源" --url "https://example.com/rss" --quality 1080p --auto-download'
        rss_commands.add(args)
        
        # 测试列出RSS源
        rss_commands.list('')
        
        # 测试显示RSS源详情
        rss_response = api_client.get(f'/api/anime/{anime_id}/rss-sources')
        if rss_response and isinstance(rss_response, list) and len(rss_response) > 0:
            rss_id = rss_response[0]['id']
            rss_commands.show(f'--id {rss_id}')
        
        print("\n[成功] RSS命令测试通过")
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
