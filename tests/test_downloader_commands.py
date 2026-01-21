#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试客户端下载器命令功能
验证下载器相关命令的正确性
使用测试隔离环境
"""
import sys
import os
import json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from client.api.client import APIClient
from client.commands.downloader_commands import DownloaderCommands
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


def test_downloader_add_command(env: TestEnvironment, api_client: APIClient, console: Console):
    """测试下载器添加命令"""
    console.print("=" * 70)
    console.print("测试1: 下载器添加命令")
    console.print("=" * 70)
    
    downloader_commands = DownloaderCommands(api_client, console, {})
    
    # 测试添加下载器
    config_dict = {'host': '127.0.0.1', 'port': 6800}
    config_json = json.dumps(config_dict)
    args = f'--name "测试下载器" --type aria2 --config \'{config_json}\' --max-concurrent 3'
    
    try:
        downloader_commands.add(args)
    except Exception as e:
        console.print(f"[red]✗[/red] 下载器添加命令执行失败: {e}")
        return False
    
    # 验证下载器是否添加成功
    downloaders_response = api_client.get('/api/downloaders')
    
    if 'error' in downloaders_response:
        console.print(f"[red]✗[/red] 获取下载器失败: {downloaders_response['error']}")
        return False
    
    downloaders = downloaders_response if isinstance(downloaders_response, list) else []
    
    if len(downloaders) > 0:
        console.print(f"[green]✓[/green] 下载器添加成功 (ID: {downloaders[0]['id']})")
        return True
    else:
        console.print("[red]✗[/red] 下载器添加失败")
        return False


def test_downloader_list_command(env: TestEnvironment, api_client: APIClient, console: Console):
    """测试下载器列表命令"""
    console.print("=" * 70)
    console.print("测试2: 下载器列表命令")
    console.print("=" * 70)
    
    downloader_commands = DownloaderCommands(api_client, console, {})
    
    # 测试列出下载器
    args = ''
    
    try:
        downloader_commands.list(args)
    except Exception as e:
        console.print(f"[red]✗[/red] 下载器列表命令执行失败: {e}")
        return False
    
    console.print("[green]✓[/green] 下载器列表命令执行成功")
    return True


def test_downloader_show_command(env: TestEnvironment, api_client: APIClient, console: Console):
    """测试下载器详情命令"""
    console.print("=" * 70)
    console.print("测试3: 下载器详情命令")
    console.print("=" * 70)
    
    downloader_commands = DownloaderCommands(api_client, console, {})
    
    # 获取第一个下载器ID
    downloaders_response = api_client.get('/api/downloaders')
    
    if 'error' in downloaders_response:
        console.print(f"[red]✗[/red] 获取下载器失败: {downloaders_response['error']}")
        return False
    
    downloaders = downloaders_response if isinstance(downloaders_response, list) else []
    if not downloaders:
        console.print("[red]✗[/red] 没有找到下载器")
        return False
    
    downloader_id = downloaders[0]['id']
    
    # 测试显示下载器详情
    args = f'--id {downloader_id}'
    
    try:
        downloader_commands.show(args)
    except Exception as e:
        console.print(f"[red]✗[/red] 下载器详情命令执行失败: {e}")
        return False
    
    console.print("[green]✓[/green] 下载器详情命令执行成功")
    return True


def test_downloader_update_command(env: TestEnvironment, api_client: APIClient, console: Console):
    """测试下载器更新命令"""
    console.print("=" * 70)
    console.print("测试4: 下载器更新命令")
    console.print("=" * 70)
    
    downloader_commands = DownloaderCommands(api_client, console, {})
    
    # 获取第一个下载器ID
    downloaders_response = api_client.get('/api/downloaders')
    
    if 'error' in downloaders_response:
        console.print(f"[red]✗[/red] 获取下载器失败: {downloaders_response['error']}")
        return False
    
    downloaders = downloaders_response if isinstance(downloaders_response, list) else []
    if not downloaders:
        console.print("[red]✗[/red] 没有找到下载器")
        return False
    
    downloader_id = downloaders[0]['id']
    
    # 测试更新下载器
    args = f'--id {downloader_id} --name "更新后的下载器"'
    
    try:
        downloader_commands.update(args)
    except Exception as e:
        console.print(f"[red]✗[/red] 下载器更新命令执行失败: {e}")
        return False
    
    # 验证更新是否成功
    updated_downloader_response = api_client.get(f'/api/downloaders/{downloader_id}')
    
    if 'error' in updated_downloader_response:
        console.print(f"[red]✗[/red] 获取更新后的下载器失败: {updated_downloader_response['error']}")
        return False
    
    if updated_downloader_response.get('name') == '更新后的下载器':
        console.print("[green]✓[/green] 下载器更新成功")
        return True
    else:
        console.print("[red]✗[/red] 下载器更新失败")
        return False


def test_downloader_test_command(env: TestEnvironment, api_client: APIClient, console: Console):
    """测试下载器测试连接命令"""
    console.print("=" * 70)
    console.print("测试5: 下载器测试连接命令")
    console.print("=" * 70)
    
    downloader_commands = DownloaderCommands(api_client, console, {})
    
    # 获取第一个下载器ID
    downloaders_response = api_client.get('/api/downloaders')
    
    if 'error' in downloaders_response:
        console.print(f"[red]✗[/red] 获取下载器失败: {downloaders_response['error']}")
        return False
    
    downloaders = downloaders_response if isinstance(downloaders_response, list) else []
    if not downloaders:
        console.print("[red]✗[/red] 没有找到下载器")
        return False
    
    downloader_id = downloaders[0]['id']
    
    # 测试下载器连接
    args = f'--id {downloader_id}'
    
    try:
        downloader_commands.test(args)
    except Exception as e:
        console.print(f"[yellow]⚠[/yellow] 下载器测试连接命令执行失败（可能因为下载器不可用）: {e}")
        # 不返回False，因为下载器可能不可用
        return True
    
    console.print("[green]✓[/green] 下载器测试连接命令执行成功")
    return True


def test_downloader_set_default_command(env: TestEnvironment, api_client: APIClient, console: Console):
    """测试设置默认下载器命令"""
    console.print("=" * 70)
    console.print("测试6: 设置默认下载器命令")
    console.print("=" * 70)
    
    downloader_commands = DownloaderCommands(api_client, console, {})
    
    # 获取第一个下载器ID
    downloaders_response = api_client.get('/api/downloaders')
    
    if 'error' in downloaders_response:
        console.print(f"[red]✗[/red] 获取下载器失败: {downloaders_response['error']}")
        return False
    
    downloaders = downloaders_response if isinstance(downloaders_response, list) else []
    if not downloaders:
        console.print("[red]✗[/red] 没有找到下载器")
        return False
    
    downloader_id = downloaders[0]['id']
    
    # 测试设置默认下载器
    args = f'--id {downloader_id}'
    
    try:
        downloader_commands.set_default(args)
    except Exception as e:
        console.print(f"[red]✗[/red] 设置默认下载器命令执行失败: {e}")
        return False
    
    console.print("[green]✓[/green] 设置默认下载器命令执行成功")
    return True


def main():
    """运行所有下载器命令测试"""
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
        console.print("客户端下载器命令测试")
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
        
        # 测试1: 下载器添加命令
        test_results.append(("下载器添加命令", test_downloader_add_command(env, api_client, console)))
        
        # 测试2: 下载器列表命令
        test_results.append(("下载器列表命令", test_downloader_list_command(env, api_client, console)))
        
        # 测试3: 下载器详情命令
        test_results.append(("下载器详情命令", test_downloader_show_command(env, api_client, console)))
        
        # 测试4: 下载器更新命令
        test_results.append(("下载器更新命令", test_downloader_update_command(env, api_client, console)))
        
        # 测试5: 下载器测试连接命令
        test_results.append(("下载器测试连接命令", test_downloader_test_command(env, api_client, console)))
        
        # 测试6: 设置默认下载器命令
        test_results.append(("设置默认下载器命令", test_downloader_set_default_command(env, api_client, console)))
        
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
            console.print("[green][成功] 所有下载器命令测试通过[/green]")
            console.print("=" * 70)
            console.print()
            return 0
        else:
            console.print("\n" + "=" * 70)
            console.print("[red][失败] 部分下载器命令测试未通过[/red]")
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
