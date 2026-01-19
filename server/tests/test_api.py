#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试服务端API功能
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import requests


def test_server_api():
    """测试服务端API"""
    print("=" * 60)
    print("测试服务端API")
    print("=" * 60)
    
    base_url = "http://127.0.0.1:8000"
    
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
        print("\n提示: 请先启动服务端: python -m server.main")
        return False
    
    # 测试智能解析
    print("\n2. 测试智能解析...")
    test_url = "https://mikanani.me/Home/Bangumi/3824"
    try:
        response = requests.post(
            f"{base_url}/api/anime/smart-parse",
            json={"url": test_url},
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
                "url": test_url,
                "auto_add_rss": False
            },
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            print("✓ 智能添加成功")
            anime = data.get('anime', {})
            print(f"  动画ID: {anime.get('id')}")
            print(f"  标题: {anime.get('title')}")
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
        response = requests.get(f"{base_url}/api/anime", timeout=5)
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
        response = requests.get(f"{base_url}/api/smart-parser/sites", timeout=5)
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


if __name__ == '__main__':
    success = test_server_api()
    sys.exit(0 if success else 1)