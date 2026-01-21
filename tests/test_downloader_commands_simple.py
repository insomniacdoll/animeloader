#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的Downloader命令测试
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.test_utils import TestEnvironment
from client.api.client import APIClient
from client.commands.downloader_commands import DownloaderCommands
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
        downloader_commands = DownloaderCommands(api_client, console, {})
        
        # 创建下载器
        downloader_response = api_client.post('/api/downloaders', json_data={
            'name': 'Mock下载器',
            'downloader_type': 'mock',
            'config': '{}',
            'is_default': True
        })
        
        if 'error' in downloader_response:
            print(f"Failed to create downloader: {downloader_response['error']}")
            return 1
        
        # 测试列出下载器
        downloader_commands.list('')
        
        # 测试显示下载器详情
        downloader_id = downloader_response['id']
        downloader_commands.show(f'--id {downloader_id}')
        
        # 测试获取支持的下载器类型
        downloader_commands.types('')
        
        print("\n[成功] Downloader命令测试通过")
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
