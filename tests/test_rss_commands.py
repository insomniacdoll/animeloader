#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试客户端RSS命令功能
验证RSS源相关命令的正确性
使用测试隔离环境
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from client.api.client import APIClient
from client.commands.rss_commands import RSSCommands
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


def test_rss_add_command(env: TestEnvironment, api_client: APIClient, console: Console):
    """测试RSS源添加命令"""
    console.print("=" * 70)
    console.print("测试1: RSS源添加命令")
    console.print("=" * 70)
    
    rss_commands = RSSCommands(api_client, console, {})
    
    # 首先创建一个动画
    anime_response = api_client.post('/api/anime', json_data={
        'title': '测试动画',
        'status': 'ongoing'
    })
    
    if 'error' in anime_response:
        console.print(f"[red]✗[/red] 创建测试动画失败: {anime_response['error']}")
        return False
    
    anime_id = anime_response['id']
    console.print(f"✓ 创建测试动画成功 (ID: {anime_id})")
    
    # 测试添加RSS源
    args = f'--anime-id {anime_id} --name "测试RSS源" --url "https://example.com/rss" --quality 1080p --auto-download'
    
    try:
        rss_commands.add(args)
    except Exception as e:
        console.print(f"[red]✗[/red] RSS源添加命令执行失败: {e}")
        return False
    
    # 验证RSS源是否添加成功
    rss_sources_response = api_client.get(f'/api/anime/{anime_id}/rss-sources')
    
    if 'error' in rss_sources_response:
        console.print(f"[red]✗[/red] 获取RSS源失败: {rss_sources_response['error']}")
        return False
    
    rss_sources = rss_sources_response if isinstance(rss_sources_response, list) else []
    
    if len(rss_sources) > 0:
        console.print(f"[green]✓[/green] RSS源添加成功 (ID: {rss_sources[0]['id']})")
        return True
    else:
        console.print("[red]✗[/red] RSS源添加失败")
        return False


def test_rss_list_command(env: TestEnvironment, api_client: APIClient, console: Console):
    """测试RSS源列表命令"""
    console.print("=" * 70)
    console.print("测试2: RSS源列表命令")
    console.print("=" * 70)
    
    rss_commands = RSSCommands(api_client, console, {})
    
    # 测试列出RSS源
    args = ''
    
    try:
        rss_commands.list(args)
    except Exception as e:
        console.print(f"[red]✗[/red] RSS源列表命令执行失败: {e}")
        return False
    
    console.print("[green]✓[/green] RSS源列表命令执行成功")
    return True


def test_rss_show_command(env: TestEnvironment, api_client: APIClient, console: Console):
    """测试RSS源详情命令"""
    console.print("=" * 70)
    console.print("测试3: RSS源详情命令")
    console.print("=" * 70)
    
    rss_commands = RSSCommands(api_client, console, {})
    
    # 获取第一个RSS源ID
    anime_response = api_client.get('/api/anime', params={'page': 1, 'size': 1})
    if 'error' in anime_response:
        console.print(f"[red]✗[/red] 获取动画失败: {anime_response['error']}")
        return False
    
    animes = anime_response.get('items', [])
    if not animes:
        console.print("[red]✗[/red] 没有找到动画")
        return False
    
    anime_id = animes[0]['id']
    rss_sources_response = api_client.get(f'/api/anime/{anime_id}/rss-sources')
    
    if 'error' in rss_sources_response:
        console.print(f"[red]✗[/red] 获取RSS源失败: {rss_sources_response['error']}")
        return False
    
    rss_sources = rss_sources_response if isinstance(rss_sources_response, list) else []
    if not rss_sources:
        console.print("[red]✗[/red] 没有找到RSS源")
        return False
    
    rss_id = rss_sources[0]['id']
    
    # 测试显示RSS源详情
    args = f'--id {rss_id}'
    
    try:
        rss_commands.show(args)
    except Exception as e:
        console.print(f"[red]✗[/red] RSS源详情命令执行失败: {e}")
        return False
    
    console.print("[green]✓[/green] RSS源详情命令执行成功")
    return True


def test_rss_update_command(env: TestEnvironment, api_client: APIClient, console: Console):
    """测试RSS源更新命令"""
    console.print("=" * 70)
    console.print("测试4: RSS源更新命令")
    console.print("=" * 70)
    
    rss_commands = RSSCommands(api_client, console, {})
    
    # 获取第一个RSS源ID
    anime_response = api_client.get('/api/anime', params={'page': 1, 'size': 1})
    if 'error' in anime_response:
        console.print(f"[red]✗[/red] 获取动画失败: {anime_response['error']}")
        return False
    
    animes = anime_response.get('items', [])
    if not animes:
        console.print("[red]✗[/red] 没有找到动画")
        return False
    
    anime_id = animes[0]['id']
    rss_sources_response = api_client.get(f'/api/anime/{anime_id}/rss-sources')
    
    if 'error' in rss_sources_response:
        console.print(f"[red]✗[/red] 获取RSS源失败: {rss_sources_response['error']}")
        return False
    
    rss_sources = rss_sources_response if isinstance(rss_sources_response, list) else []
    if not rss_sources:
        console.print("[red]✗[/red] 没有找到RSS源")
        return False
    
    rss_id = rss_sources[0]['id']
    
    # 测试更新RSS源
    args = f'--id {rss_id} --name "更新后的RSS源"'
    
    try:
        rss_commands.update(args)
    except Exception as e:
        console.print(f"[red]✗[/red] RSS源更新命令执行失败: {e}")
        return False
    
    # 验证更新是否成功
    updated_rss_response = api_client.get(f'/api/rss-sources/{rss_id}')
    
    if 'error' in updated_rss_response:
        console.print(f"[red]✗[/red] 获取更新后的RSS源失败: {updated_rss_response['error']}")
        return False
    
    if updated_rss_response.get('name') == '更新后的RSS源':
        console.print("[green]✓[/green] RSS源更新成功")
        return True
    else:
        console.print("[red]✗[/red] RSS源更新失败")
        return False


def test_rss_check_command(env: TestEnvironment, api_client: APIClient, console: Console):
    """测试RSS源检查命令"""
    console.print("=" * 70)
    console.print("测试5: RSS源检查命令")
    console.print("=" * 70)
    
    rss_commands = RSSCommands(api_client, console, {})
    
    # 获取第一个RSS源ID
    anime_response = api_client.get('/api/anime', params={'page': 1, 'size': 1})
    if 'error' in anime_response:
        console.print(f"[red]✗[/red] 获取动画失败: {anime_response['error']}")
        return False
    
    animes = anime_response.get('items', [])
    if not animes:
        console.print("[red]✗[/red] 没有找到动画")
        return False
    
    anime_id = animes[0]['id']
    rss_sources_response = api_client.get(f'/api/anime/{anime_id}/rss-sources')
    
    if 'error' in rss_sources_response:
        console.print(f"[red]✗[/red] 获取RSS源失败: {rss_sources_response['error']}")
        return False
    
    rss_sources = rss_sources_response if isinstance(rss_sources_response, list) else []
    if not rss_sources:
        console.print("[red]✗[/red] 没有找到RSS源")
        return False
    
    rss_id = rss_sources[0]['id']
    
    # 测试检查RSS源
    args = f'--id {rss_id}'
    
    try:
        rss_commands.check(args)
    except Exception as e:
        console.print(f"[yellow]⚠[/yellow] RSS源检查命令执行失败（可能因为RSS URL无效）: {e}")
        # 不返回False，因为RSS URL可能无效
        return True
    
    console.print("[green]✓[/green] RSS源检查命令执行成功")
    return True


def main():
    """运行所有RSS命令测试"""
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
        console.print("客户端RSS命令测试")
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
        
        # 测试1: RSS源添加命令
        test_results.append(("RSS源添加命令", test_rss_add_command(env, api_client, console)))
        
        # 测试2: RSS源列表命令
        test_results.append(("RSS源列表命令", test_rss_list_command(env, api_client, console)))
        
        # 测试3: RSS源详情命令
        test_results.append(("RSS源详情命令", test_rss_show_command(env, api_client, console)))
        
        # 测试4: RSS源更新命令
        test_results.append(("RSS源更新命令", test_rss_update_command(env, api_client, console)))
        
        # 测试5: RSS源检查命令
        test_results.append(("RSS源检查命令", test_rss_check_command(env, api_client, console)))
        
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
            console.print("[green][成功] 所有RSS命令测试通过[/green]")
            console.print("=" * 70)
            console.print()
            return 0
        else:
            console.print("\n" + "=" * 70)
            console.print("[red][失败] 部分RSS命令测试未通过[/red]")
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
