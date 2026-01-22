#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
运行所有测试
所有测试都使用隔离环境，自动启动和停止服务端
"""
import sys
import os
import subprocess

def run_command(cmd, description):
    """运行命令并返回结果"""
    print(f"\n{'=' * 60}")
    print(f"运行: {description}")
    print(f"{'=' * 60}")
    result = subprocess.run(cmd, shell=True, capture_output=False, text=True)
    return result.returncode == 0

def main():
    """主函数"""
    print("=" * 60)
    print("运行所有测试")
    print("=" * 60)
    
    results = []
    
    # 激活虚拟环境
    venv_python = "venv/bin/python"
    if not os.path.exists(venv_python):
        print(f"[错误] 虚拟环境不存在: {venv_python}")
        return False
    
    # 不需要服务端的测试
    # 测试1: 蜜柑计划解析器（不需要服务端）
    results.append(run_command(
        f"{venv_python} tests/test_smart_parser.py",
        "蜜柑计划解析器测试"
    ))
    
    # 测试2: 链接服务测试（不需要服务端）
    results.append(run_command(
        f"{venv_python} tests/test_link_service.py",
        "链接服务测试"
    ))
    
    # 测试3: 下载器服务测试（不需要服务端）
    results.append(run_command(
        f"{venv_python} tests/test_downloader_service.py",
        "下载器服务测试"
    ))
    
    # 测试4: 下载服务测试（不需要服务端）
    results.append(run_command(
        f"{venv_python} tests/test_download_service.py",
        "下载服务测试"
    ))
    
    # 测试5: 调度服务测试（不需要服务端）
    results.append(run_command(
        f"{venv_python} tests/test_scheduler_service.py",
        "调度服务测试"
    ))
    
    # 需要服务端的测试（使用隔离环境，自动启动和停止）
    # 测试6: 服务端API测试
    results.append(run_command(
        f"{venv_python} tests/test_api.py",
        "服务端API测试"
    ))
    
    # 测试7: 智能添加测试
    results.append(run_command(
        f"{venv_python} tests/test_smart_add.py",
        "智能添加测试"
    ))
    
    # 测试8: 客户端API认证测试
    results.append(run_command(
        f"{venv_python} tests/test_auth.py",
        "客户端API认证测试"
    ))
    
    # 新增的客户端命令导入测试
    # 测试9: 命令模块导入测试
    results.append(run_command(
        f"{venv_python} tests/test_commands_import.py",
        "命令模块导入测试"
    ))
    
    # 新增的重复预防测试
    # 测试10: 服务层重复添加预防测试
    results.append(run_command(
        f"{venv_python} tests/test_duplicate_prevention.py",
        "服务层重复添加预防测试"
    ))
    
    # 测试11: API层重复添加预防测试
    results.append(run_command(
        f"{venv_python} tests/test_api_duplicate.py",
        "API层重复添加预防测试"
    ))
    
    # 汇总结果
    print(f"\n{'=' * 60}")
    print("测试结果汇总")
    print(f"{'=' * 60}")
    
    test_names = [
        "蜜柑计划解析器测试",
        "链接服务测试",
        "下载器服务测试",
        "下载服务测试",
        "调度服务测试",
        "服务端API测试",
        "智能添加测试",
        "客户端API认证测试",
        "命令模块导入测试",
        "服务层重复添加预防测试",
        "API层重复添加预防测试"
    ]
    
    for i, (name, result) in enumerate(zip(test_names, results), 1):
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{i}. {name}: {status}")
    
    all_passed = all(results)
    print(f"\n{'=' * 60}")
    if all_passed:
        print("[成功] 所有测试通过")
    else:
        print("[失败] 部分测试失败")
    print(f"{'=' * 60}")
    
    return all_passed

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
