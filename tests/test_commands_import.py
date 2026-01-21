#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试命令模块导入
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def main():
    print("测试导入所有命令模块...")
    
    try:
        from client.commands.rss_commands import RSSCommands
        print("✓ RSSCommands 导入成功")
    except Exception as e:
        print(f"✗ RSSCommands 导入失败: {e}")
        return 1
    
    try:
        from client.commands.link_commands import LinkCommands
        print("✓ LinkCommands 导入成功")
    except Exception as e:
        print(f"✗ LinkCommands 导入失败: {e}")
        return 1
    
    try:
        from client.commands.downloader_commands import DownloaderCommands
        print("✓ DownloaderCommands 导入成功")
    except Exception as e:
        print(f"✗ DownloaderCommands 导入失败: {e}")
        return 1
    
    try:
        from client.commands.download_commands import DownloadCommands
        print("✓ DownloadCommands 导入成功")
    except Exception as e:
        print(f"✗ DownloadCommands 导入失败: {e}")
        return 1
    
    try:
        from client.commands.status_commands import StatusCommands
        print("✓ StatusCommands 导入成功")
    except Exception as e:
        print(f"✗ StatusCommands 导入失败: {e}")
        return 1
    
    print("\n[成功] 所有命令模块导入成功")
    return 0

if __name__ == '__main__':
    sys.exit(main())
