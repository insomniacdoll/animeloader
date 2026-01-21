#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
运行所有测试
"""
import sys
import os
import subprocess
import time

def run_command(cmd, description):
    """运行命令并返回结果"""
    print(f"\n{'=' * 60}")
    print(f"运行: {description}")
    print(f"{'=' * 60}")
    result = subprocess.run(cmd, shell=True, capture_output=False)
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
    
    # 测试1: 蜜柑计划解析器（不需要服务端）
    results.append(run_command(
        f"{venv_python} server/tests/test_smart_parser.py",
        "蜜柑计划解析器测试"
    ))
    
    # 测试2: 智能添加测试（不需要服务端）
    results.append(run_command(
        f"{venv_python} server/tests/test_smart_add.py",
        "智能添加测试"
    ))
    
    # 测试3: 链接服务测试（不需要服务端）
    results.append(run_command(
        f"{venv_python} server/tests/test_link_service.py",
        "链接服务测试"
    ))
    
    # 测试4: 下载器服务测试（不需要服务端）
    results.append(run_command(
        f"{venv_python} server/tests/test_downloader_service.py",
        "下载器服务测试"
    ))
    
    # 测试5: 下载服务测试（不需要服务端）
    results.append(run_command(
        f"{venv_python} server/tests/test_download_service.py",
        "下载服务测试"
    ))
    
    # 测试6: 调度服务测试（不需要服务端）
    results.append(run_command(
        f"{venv_python} server/tests/test_scheduler_service.py",
        "调度服务测试"
    ))
    
    # 启动服务端
    print(f"\n{'=' * 60}")
    print("启动服务端...")
    print(f"{'=' * 60}")
    server_process = subprocess.Popen(
        f"{venv_python} -m server.main --config server_config.yaml",
        shell=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    time.sleep(3)
    
    try:
        # 测试7: 服务端API测试
        results.append(run_command(
            f"{venv_python} server/tests/test_api.py",
            "服务端API测试"
        ))
        
        # 测试8: 客户端测试
        results.append(run_command(
            f"{venv_python} client/tests/test_smart_add.py",
            "客户端测试"
        ))
        
        # 测试9: 客户端API认证测试
        results.append(run_command(
            f"{venv_python} client/tests/test_auth.py",
            "客户端API认证测试"
        ))
        
    finally:
        # 停止服务端
        print(f"\n{'=' * 60}")
        print("停止服务端...")
        print(f"{'=' * 60}")
        server_process.terminate()
        server_process.wait(timeout=5)
        # 强制杀死
        subprocess.run("lsof -ti:8000 | xargs kill -9 2>/dev/null || true", shell=True)
    
    # 汇总结果
    print(f"\n{'=' * 60}")
    print("测试结果汇总")
    print(f"{'=' * 60}")
    
    test_names = [
        "蜜柑计划解析器测试",
        "智能添加测试",
        "链接服务测试",
        "下载器服务测试",
        "下载服务测试",
        "调度服务测试",
        "服务端API测试",
        "客户端测试",
        "客户端API认证测试"
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