#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试客户端链接命令功能
验证链接相关命令的正确性
使用测试隔离环境
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from client.api.client import APIClient
from client.commands.link_commands import LinkCommands
from rich.console import Console
from rich.table import Table
from tests.test_utils import TestEnvironment


def get_default_api_key(env: TestEnvironment):
    """获取默认API密钥"""
    try:
        from server.utils import init_config
        from server.database import get_db, get_engine
        from server.services.api_key_service import APIKeyService
        from server.models import Base
        
        init_config(env.get_config_path())
        
        engine = get_engine()
        Base.metadata.create_all(bind=engine)
        
        SessionLocal = next(get_db())
        try:
            api_key_service = APIKeyService(SessionLocal)
            default_key = api_key_service.get_default_api_key()
            return default_key.key if default_key else None
        finally:
            SessionLocal.close()
    except Exception as e:
        print(f"获取API密钥失败: {e}")
        return None


def test_link_list_command(env: TestEnvironment, api_client: APIClient, console: Console):
    """测试链接列表命令"""
    console.print("=" * 70)
    console.print("测试1: 链接列表命令")
    console.print("=" * 70)
    
    link_commands = LinkCommands(api_client, console, {})
    
    # 测试列出链接
    args = ''
    
    try:
        link_commands.list(args)
    except Exception as e:
        console.print(f"[red]✗[/red] 链接列表命令执行失败: {e}")
        return False
    
    console.print("[green]✓[/green] 链接列表命令执行成功")
    return True


def test_link_show_command(env: TestEnvironment, api_client: APIClient, console: Console):
    """测试链接详情命令"""
    console.print("=" * 70)
    console.print("测试2: 链接详情命令")
    console.print("=" * 70)
    
    link_commands = LinkCommands(api_client, console, {})
    
    # 首先创建测试数据
    # 创建动画
    anime_response = api_client.post('/api/anime', json_data={
        'title': '测试动画',
        'status': 'ongoing'
    })
    
    if 'error' in anime_response:
        console.print(f"[red]✗[/red] 创建测试动画失败: {anime_response['error']}")
        return False
    
    anime_id = anime_response['id']
    
    # 创建RSS源
    rss_response = api_client.post('/api/rss-sources', json_data={
        'anime_id': anime_id,
        'name': '测试RSS源',
        'url': 'https://example.com/rss',
        'is_active': True,
        'auto_download': False
    })
    
    if 'error' in rss_response:
        console.print(f"[red]✗[/red] 创建测试RSS源失败: {rss_response['error']}")
        return False
    
    rss_id = rss_response['id']
    
    # 创建链接
    link_response = api_client.post('/api/links', json_data={
        'rss_source_id': rss_id,
        'episode_number': 1,
        'episode_title': '第1集',
        'link_type': 'magnet',
        'url': 'magnet:?xt=urn:btih:test',
        'file_size': 1024000,
        'publish_date': '2024-01-01T00:00:00',
        'is_downloaded': False,
        'is_available': True
    })
    
    if 'error' in link_response:
        console.print(f"[red]✗[/red] 创建测试链接失败: {link_response['error']}")
        return False
    
    link_id = link_response['id']
    console.print(f"✓ 创建测试链接成功 (ID: {link_id})")
    
    # 测试显示链接详情
    args = f'--id {link_id}'
    
    try:
        link_commands.show(args)
    except Exception as e:
        console.print(f"[red]✗[/red] 链接详情命令执行失败: {e}")
        return False
    
    console.print("[green]✓[/green] 链接详情命令执行成功")
    return True


def test_link_mark_downloaded_command(env: TestEnvironment, api_client: APIClient, console: Console):
    """测试标记链接为已下载命令"""
    console.print("=" * 70)
    console.print("测试3: 标记链接为已下载命令")
    console.print("=" * 70)
    
    link_commands = LinkCommands(api_client, console, {})
    
    # 获取第一个链接ID
    links_response = api_client.get('/api/links', params={'page': 1, 'size': 1})
    
    if 'error' in links_response:
        console.print(f"[red]✗[/red] 获取链接失败: {links_response['error']}")
        return False
    
    links = links_response.get('items', [])
    if not links:
        console.print("[red]✗[/red] 没有找到链接")
        return False
    
    link_id = links[0]['id']
    
    # 测试标记链接为已下载
    args = f'--id {link_id}'
    
    try:
        link_commands.mark_downloaded(args)
    except Exception as e:
        console.print(f"[red]✗[/red] 标记链接为已下载命令执行失败: {e}")
        return False
    
    # 验证标记是否成功
    updated_link_response = api_client.get(f'/api/links/{link_id}')
    
    if 'error' in updated_link_response:
        console.print(f"[red]✗[/red] 获取更新后的链接失败: {updated_link_response['error']}")
        return False
    
    if updated_link_response.get('is_downloaded'):
        console.print("[green]✓[/green] 标记链接为已下载成功")
        return True
    else:
        console.print("[red]✗[/red] 标记链接为已下载失败")
        return False


def main():
    """运行所有链接命令测试"""
    env = TestEnvironment()
    try:
        env.setup()
        
        # 启动服务端
        if not env.start_server():
            print("✗ 服务端启动失败")
            return 1
        
        console = Console()
        
        console.print("\n")
        console.print("=" * 70)
        console.print("客户端链接命令测试")
        console.print("=" * 70)
        console.print()
        
        # 获取API密钥
        api_key = get_default_api_key(env)
        if not api_key:
            console.print("[red]✗[/red] 无法获取有效的API密钥")
            return 1
        
        # 创建API客户端
        api_client = APIClient(base_url=env.get_server_url(), api_key=api_key)
        
        # 运行所有测试
        test_results = []
        
        # 测试1: 链接列表命令
        test_results.append(("链接列表命令", test_link_list_command(env, api_client, console)))
        
        # 测试2: 链接详情命令
        test_results.append(("链接详情命令", test_link_show_command(env, api_client, console)))
        
        # 测试3: 标记链接为已下载命令
        test_results.append(("标记链接为已下载命令", test_link_mark_downloaded_command(env, api_client, console)))
        
        # 显示汇总结果
        console.print("=" * 70)
        console.print("测试结果汇总")
        console.print("=" * 70)
        
        table = Table()
        table.add_column("测试项", style="cyan")
        table.add_column("结果", style="green")
        
        all_passed = True
        for test_name, result in test_results:
            status = "✓ 通过" if result else "✗ 失败"
            color = "green" if result else "red"
            table.add_row(test_name, f"[{color}]{status}[/{color}]")
            if not result:
                all_passed = False
        
        console.print(table)
        
        if all_passed:
            console.print("\n" + "=" * 70)
            console.print("[green][成功] 所有链接命令测试通过[/green]")
            console.print("=" * 70)
            console.print()
            return 0
        else:
            console.print("\n" + "=" * 70)
            console.print("[red][失败] 部分链接命令测试未通过[/red]")
            console.print("=" * 70)
            console.print()
            return 1
    except Exception as e:
        print(f"\n[失败] 发生错误: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        env.teardown()


if __name__ == '__main__':
    sys.exit(main())
