#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试服务端API功能
使用测试隔离环境
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
from tests.test_utils import TestEnvironment


def get_default_api_key(env: TestEnvironment):
    """获取默认API密钥"""
    try:
        from server.utils import init_config
        from server.database import get_db, get_engine
        from server.services.api_key_service import APIKeyService
        from server.models import Base
        
        # 初始化配置（使用测试环境的配置文件）
        init_config(env.get_config_path())
        
        # 初始化数据库
        engine = get_engine()
        Base.metadata.create_all(bind=engine)
        
        # 获取数据库会话
        SessionLocal = next(get_db())
        try:
            api_key_service = APIKeyService(SessionLocal)
            default_key = api_key_service.get_default_api_key()
            return default_key.key if default_key else None
        finally:
            SessionLocal.close()
    except Exception as e:
        print(f"获取API密钥失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_server_api(env: TestEnvironment):
    """测试服务端API"""
    print("=" * 60)
    print("测试服务端API")
    print("=" * 60)
    
    # 打印测试环境信息
    env.print_info()
    
    # 启动服务端
    if not env.start_server():
        print("✗ 服务端启动失败")
        return False
    
    base_url = env.get_server_url()
    headers = {}
    
    # 获取API密钥
    print("\n0. 获取默认API密钥...")
    api_key = get_default_api_key(env)
    if api_key:
        headers['X-API-Key'] = api_key
        print(f"✓ 获取API密钥成功: {api_key}")
    else:
        print("✗ 获取API密钥失败，将尝试不带API密钥的请求")
    
    # 测试健康检查
    print("\n1. 测试健康检查...")
    try:
        response = requests.get(f"{base_url}/api/health", timeout=5)
        if response.status_code == 200:
            print("✓ 健康检查通过")
            print(f"  响应: {response.json()}")
        else:
            print(f"✗ 健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ 健康检查失败: {e}")
        return False
    
    # 测试智能解析
    print("\n2. 测试智能解析...")
    test_url = "https://mikanani.me/Home/Bangumi/3824"
    try:
        response = requests.post(
            f"{base_url}/api/anime/smart-parse",
            json={"url": test_url},
            headers=headers,
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            print("✓ 智能解析成功")
            print(f"  网站名称: {data.get('site_name', '')}")
            print(f"  解析结果数: {len(data.get('results', []))}")
            if data.get('results'):
                anime = data['results'][0]
                print(f"  标题: {anime.get('title', '')}")
                print(f"  RSS源数: {len(anime.get('rss_sources', []))}")
        else:
            print(f"✗ 智能解析失败: {response.status_code}")
            print(f"  响应: {response.text}")
            return False
    except Exception as e:
        print(f"✗ 智能解析失败: {e}")
        return False
    
    # 测试智能添加
    print("\n3. 测试智能添加...")
    try:
        response = requests.post(
            f"{base_url}/api/anime/smart-add",
            json={
                'url': test_url,
                'auto_add_rss': False,
                'anime_index': 1,
                'rss_indices': []
            },
            headers=headers,
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            print("✓ 智能添加成功")
            anime = data.get('anime', {})
            print(f"  标题: {anime.get('title', '')}")
            print(f"  RSS源数: {len(data.get('rss_sources', []))}")
        else:
            print(f"✗ 智能添加失败: {response.status_code}")
            print(f"  响应: {response.text}")
            return False
    except Exception as e:
        print(f"✗ 智能添加失败: {e}")
        return False
    
    # 测试获取动画列表
    print("\n4. 测试获取动画列表...")
    try:
        response = requests.get(f"{base_url}/api/anime", headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✓ 获取动画列表成功")
            print(f"  总数: {data.get('total', 0)}")
            for anime in data.get('items', [])[:3]:
                print(f"    - {anime.get('title')} (ID: {anime.get('id')})")
        else:
            print(f"✗ 获取动画列表失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ 获取动画列表失败: {e}")
        return False
    
    # 测试获取支持的网站
    print("\n5. 测试获取支持的网站...")
    try:
        response = requests.get(f"{base_url}/api/smart-parser/sites", headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✓ 获取支持的网站成功")
            print(f"  消息: {data.get('message', '')}")
        else:
            print(f"✗ 获取支持的网站失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ 获取支持的网站失败: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("[成功] 所有测试通过")
    print("=" * 60)
    return True


def main():
    """主函数"""
    env = TestEnvironment()
    try:
        env.setup()
        success = test_server_api(env)
        return 0 if success else 1
    except Exception as e:
        print(f"\n[失败] 发生错误: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        env.teardown()


if __name__ == '__main__':
    sys.exit(main())
