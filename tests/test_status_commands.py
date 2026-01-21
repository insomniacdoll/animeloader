#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试客户端状态命令功能
验证状态查询相关命令的正确性
使用测试隔离环境
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from client.api.client import APIClient
from client.commands.status_commands import StatusCommands
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


def test_status_server_command(env: TestEnvironment, api_client: APIClient, console: Console):
    """测试查看服务器状态命令"""
    console.print("=" * 70)
    console.print("测试1: 查看服务器状态命令")
    console.print("=" * 70)
    
    status_commands = StatusCommands(api_client, console, {})
    
    # 测试查看服务器状态
    args = ''
    
    try:
        status_commands.server(args)
    except Exception as e:
        console.print(f"[red]✗[/red] 查看服务器状态命令执行失败: {e}")
        return False
    
    console.print("[green]✓[/green] 查看服务器状态命令执行成功")
    return True


def test_status_system_command(env: TestEnvironment, api_client: APIClient, console: Console):
    """测试查看系统信息命令"""
    console.print("=" * 70)
    console.print("测试2: 查看系统信息命令")
    console.print("=" * 70)
    
    status_commands = StatusCommands(api_client, console, {})
    
    # 测试查看系统信息
    args = ''
    
    try:
        status_commands.system(args)
    except Exception as e:
        console.print(f"[red]✗[/red] 查看系统信息命令执行失败: {e}")
        return False
    
    console.print("[green]✓[/green] 查看系统信息命令执行成功")
    return True


def test_status_scheduler_command(env: TestEnvironment, api_client: APIClient, console: Console):
    """测试查看调度器状态命令"""
    console.print("=" * 70)
    console.print("测试3: 查看调度器状态命令")
    console.print("=" * 70)
    
    status_commands = StatusCommands(api_client, console, {})
    
    # 测试查看调度器状态
    args = ''
    
    try:
        status_commands.scheduler(args)
    except Exception as e:
        console.print(f"[red]✗[/red] 查看调度器状态命令执行失败: {e}")
        return False
    
    console.print("[green]✓[/green] 查看调度器状态命令执行成功")
    return True


def test_status_summary_command(env: TestEnvironment, api_client: APIClient, console: Console):
    """测试查看系统摘要命令"""
    console.print("=" * 70)
    console.print("测试4: 查看系统摘要命令")
    console.print("=" * 70)
    
    status_commands = StatusCommands(api_client, console, {})
    
    # 测试查看系统摘要
    args = ''
    
    try:
        status_commands.summary(args)
    except Exception as e:
        console.print(f"[red]✗[/red] 查看系统摘要命令执行失败: {e}")
        return False
    
    console.print("[green]✓[/green] 查看系统摘要命令执行成功")
    return True


def main():
    """运行所有状态命令测试"""
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
        console.print("客户端状态命令测试")
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
        
        # 测试1: 查看服务器状态命令
        test_results.append(("查看服务器状态命令", test_status_server_command(env, api_client, console)))
        
        # 测试2: 查看系统信息命令
        test_results.append(("查看系统信息命令", test_status_system_command(env, api_client, console)))
        
        # 测试3: 查看调度器状态命令
        test_results.append(("查看调度器状态命令", test_status_scheduler_command(env, api_client, console)))
        
        # 测试4: 查看系统摘要命令
        test_results.append(("查看系统摘要命令", test_status_summary_command(env, api_client, console)))
        
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
            console.print("[green][成功] 所有状态命令测试通过[/green]")
            console.print("=" * 70)
            console.print()
            return 0
        else:
            console.print("\n" + "=" * 70)
            console.print("[red][失败] 部分状态命令测试未通过[/red]")
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