#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试客户端API认证功能
验证没有API密钥或无效API密钥时无法访问API
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from client.api.client import APIClient
from rich.console import Console
from rich.table import Table


def get_default_api_key():
    """获取默认API密钥"""
    try:
        from server.utils.config import init_config
        from server.database import get_db, get_engine
        from server.services.api_key_service import APIKeyService
        from server.models import Base
        
        # 初始化配置
        init_config()
        
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
        return None


def test_no_api_key():
    """测试没有API密钥时访问API"""
    console = Console()
    
    console.print("=" * 70)
    console.print("测试1: 没有API密钥时访问API")
    console.print("=" * 70)
    
    # 创建没有API密钥的客户端
    api_client = APIClient(base_url="http://127.0.0.1:8000", api_key=None)
    
    # 测试各种API端点（健康检查不需要认证）
    test_cases = [
        ("GET", "/api/health", "健康检查", False),  # False表示不需要认证
        ("GET", "/api/anime", "获取动画列表", True),
        ("POST", "/api/anime/smart-parse", "智能解析动画", True),
        ("GET", "/api/rss-sources", "获取RSS源列表", True),
        ("GET", "/api/links", "获取链接列表", True),
        ("GET", "/api/downloaders", "获取下载器列表", True),
        ("GET", "/api/downloads", "获取下载任务列表", True),
        ("GET", "/api/scheduler/jobs", "获取调度任务", True),
        ("GET", "/api/smart-parser/sites", "获取支持的网站", True),
    ]
    
    results = []
    for method, endpoint, description, requires_auth in test_cases:
        try:
            if method == "GET":
                response = api_client.get(endpoint)
            elif method == "POST":
                response = api_client.post(endpoint, json_data={'url': 'https://example.com'})
            
            # 检查响应
            if 'error' in response:
                # 可能是连接错误或HTTP错误
                if requires_auth:
                    success = '401' in str(response.get('error', '')) or 'Unauthorized' in str(response.get('error', ''))
                    status = "✓ 成功拒绝" if success else "✗ 错误"
                    results.append((description, status, response.get('error', 'Unknown error')))
                    if not success:
                        all_passed = False
                else:
                    # 不需要认证的端点，不应该有错误
                    status = "✗ 失败（应该成功）"
                    results.append((description, status, response.get('error', 'Unknown error')))
                    all_passed = False
            else:
                # 没有错误
                if requires_auth:
                    # 需要认证的端点成功了（不应该发生）
                    status = "✗ 失败（应该被拒绝）"
                    results.append((description, status, "请求成功但应该被拒绝"))
                    all_passed = False
                else:
                    # 不需要认证的端点成功了（正确）
                    status = "✓ 成功（无需认证）"
                    results.append((description, status, "请求成功"))
        except Exception as e:
            error_str = str(e)
            if requires_auth:
                success = '401' in error_str or 'Unauthorized' in error_str
                status = "✓ 成功拒绝" if success else "✗ 错误"
                results.append((description, status, error_str))
                if not success:
                    all_passed = False
            else:
                # 不需要认证的端点，不应该有异常
                status = "✗ 失败（应该成功）"
                results.append((description, status, error_str))
                all_passed = False
    
    # 显示结果
    table = Table(title="测试结果")
    table.add_column("API端点", style="cyan")
    table.add_column("结果", style="green")
    table.add_column("错误信息", style="yellow")
    
    all_passed = True
    for description, status, error in results:
        color = "green" if "成功" in status else "red"
        table.add_row(description, f"[{color}]{status}[/{color}]", error[:50] + "..." if len(error) > 50 else error)
        if "失败" in status:
            all_passed = False
    
    console.print(table)
    
    if all_passed:
        console.print("\n[green]✓[/green] 所有请求均被正确处理")
    else:
        console.print("\n[red]✗[/red] 部分请求未被正确处理")
    
    console.print()
    return all_passed


def test_invalid_api_key():
    """测试无效的API密钥"""
    console = Console()
    
    console.print("=" * 70)
    console.print("测试2: 使用无效的API密钥")
    console.print("=" * 70)
    
    # 创建使用无效API密钥的客户端
    invalid_api_key = "00000000-0000-0000-0000-000000000000"
    api_client = APIClient(base_url="http://127.0.0.1:8000", api_key=invalid_api_key)
    
    console.print(f"使用的无效API密钥: {invalid_api_key}")
    console.print()
    
    # 测试各种API端点
    test_cases = [
        ("GET", "/api/anime", "获取动画列表"),
        ("GET", "/api/rss-sources", "获取RSS源列表"),
        ("GET", "/api/links", "获取链接列表"),
    ]
    
    results = []
    for method, endpoint, description in test_cases:
        try:
            if method == "GET":
                response = api_client.get(endpoint)
            
            # 检查响应
            if 'error' in response:
                success = '401' in str(response.get('error', '')) or 'Unauthorized' in str(response.get('error', ''))
                status = "✓ 成功拒绝" if success else "✗ 错误"
                results.append((description, status, response.get('error', 'Unknown error')))
            else:
                status = "✗ 失败（应该被拒绝）"
                results.append((description, status, "请求成功但应该被拒绝"))
        except Exception as e:
            error_str = str(e)
            success = '401' in error_str or 'Unauthorized' in error_str
            status = "✓ 成功拒绝" if success else "✗ 错误"
            results.append((description, status, error_str))
    
    # 显示结果
    table = Table(title="测试结果")
    table.add_column("API端点", style="cyan")
    table.add_column("结果", style="green")
    table.add_column("错误信息", style="yellow")
    
    all_passed = True
    for description, status, error in results:
        color = "green" if "成功" in status else "red"
        table.add_row(description, f"[{color}]{status}[/{color}]", error[:50] + "..." if len(error) > 50 else error)
        if "失败" in status:
            all_passed = False
    
    console.print(table)
    
    if all_passed:
        console.print("\n[green]✓[/green] 所有请求均被正确拒绝")
    else:
        console.print("\n[red]✗[/red] 部分请求未被正确拒绝")
    
    console.print()
    return all_passed


def test_valid_api_key():
    """测试有效的API密钥"""
    console = Console()
    
    console.print("=" * 70)
    console.print("测试3: 使用有效的API密钥")
    console.print("=" * 70)
    
    # 获取有效的API密钥
    api_key = get_default_api_key()
    
    if not api_key:
        console.print("[red]✗[/red] 无法获取有效的API密钥")
        console.print()
        return False
    
    console.print(f"使用的有效API密钥: {api_key}")
    console.print()
    
    # 创建使用有效API密钥的客户端
    api_client = APIClient(base_url="http://127.0.0.1:8000", api_key=api_key)
    
    # 测试各种API端点
    test_cases = [
        ("GET", "/api/health", "健康检查"),
        ("GET", "/api/anime", "获取动画列表"),
        ("GET", "/api/smart-parser/sites", "获取支持的网站"),
        ("GET", "/api/rss-sources", "获取RSS源列表"),
    ]
    
    results = []
    for method, endpoint, description in test_cases:
        try:
            if method == "GET":
                response = api_client.get(endpoint)
            
            # 检查响应
            if 'error' in response:
                status = "✗ 失败"
                results.append((description, status, response.get('error', 'Unknown error')))
            else:
                status = "✓ 成功"
                # 显示响应摘要
                if 'message' in response:
                    summary = response['message']
                elif 'total' in response:
                    summary = f"共 {response['total']} 条记录"
                else:
                    summary = "请求成功"
                results.append((description, status, summary))
        except Exception as e:
            status = "✗ 失败"
            results.append((description, status, str(e)))
    
    # 显示结果
    table = Table(title="测试结果")
    table.add_column("API端点", style="cyan")
    table.add_column("结果", style="green")
    table.add_column("响应", style="yellow")
    
    all_passed = True
    for description, status, response in results:
        color = "green" if "成功" in status else "red"
        table.add_row(description, f"[{color}]{status}[/{color}]", response[:50] + "..." if len(response) > 50 else response)
        if "失败" in status:
            all_passed = False
    
    console.print(table)
    
    if all_passed:
        console.print("\n[green]✓[/green] 所有请求均成功")
    else:
        console.print("\n[red]✗[/red] 部分请求失败")
    
    console.print()
    return all_passed


def test_empty_api_key():
    """测试空的API密钥"""
    console = Console()
    
    console.print("=" * 70)
    console.print("测试4: 使用空的API密钥")
    console.print("=" * 70)
    
    # 创建使用空API密钥的客户端
    api_client = APIClient(base_url="http://127.0.0.1:8000", api_key="")
    
    console.print("使用的空API密钥: \"\"\"")
    console.print()
    
    # 测试API端点
    try:
        response = api_client.get("/api/anime")
        
        # 检查响应
        if 'error' in response:
            success = '401' in str(response.get('error', '')) or 'Unauthorized' in str(response.get('error', ''))
            status = "✓ 成功拒绝" if success else "✗ 错误"
            console.print(f"[{'green' if success else 'red'}]{status}[/{success and 'green' or 'red'}]")
            console.print(f"错误信息: {response.get('error', 'Unknown error')}")
            return success
        else:
            console.print("[red]✗ 失败（应该被拒绝）[/red]")
            console.print("请求成功但应该被拒绝")
            return False
    except Exception as e:
        error_str = str(e)
        success = '401' in error_str or 'Unauthorized' in error_str
        status = "✓ 成功拒绝" if success else "✗ 错误"
        console.print(f"[{'green' if success else 'red'}]{status}[/{success and 'green' or 'red'}]")
        console.print(f"错误信息: {error_str}")
        console.print()
        return success


def main():
    """运行所有认证测试"""
    console = Console()
    
    console.print("\n")
    console.print("=" * 70)
    console.print("客户端API认证测试")
    console.print("=" * 70)
    console.print()
    
    # 运行所有测试
    test_results = []
    
    # 测试1: 没有API密钥
    test_results.append(("没有API密钥", test_no_api_key()))
    
    # 测试2: 无效的API密钥
    test_results.append(("无效的API密钥", test_invalid_api_key()))
    
    # 测试3: 空的API密钥
    test_results.append(("空的API密钥", test_empty_api_key()))
    
    # 测试4: 有效的API密钥
    test_results.append(("有效的API密钥", test_valid_api_key()))
    
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
        console.print("[green][成功] 所有认证测试通过[/green]")
        console.print("=" * 70)
        console.print()
        return 0
    else:
        console.print("\n" + "=" * 70)
        console.print("[red][失败] 部分认证测试未通过[/red]")
        console.print("=" * 70)
        console.print()
        return 1


if __name__ == '__main__':
    sys.exit(main())