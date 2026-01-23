#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AnimeLoader 二进制打包脚本
用于将服务端和客户端分别打包成独立的可执行文件
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def install_pyinstaller():
    """安装 PyInstaller"""
    print("正在安装 PyInstaller...")
    result = subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], 
                          capture_output=True, text=True)
    if result.returncode != 0:
        print("安装 PyInstaller 失败: {}".format(result.stderr))
        return False
    print("PyInstaller 安装成功")
    return True


def build_server(output_dir="dist"):
    """打包服务端程序"""
    print("开始打包服务端...")
    
    # 创建一个临时的服务器入口脚本
    server_entry_point = "server_standalone.py"
    with open(server_entry_point, "w", encoding="utf-8") as f:
        f.write('''#!/usr/bin/env python3
"""
AnimeLoader 服务端独立运行入口
"""
import sys
import os

# 添加项目根目录到 Python 路径
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# 导入并运行服务器主函数
from server.main import main

if __name__ == "__main__":
    main()
''')
    
    try:
        # 使用 PyInstaller 打包服务端
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--name", "animeloader-server",
            "--onefile",
            "--distpath", output_dir,
            "--clean",
            "--hidden-import=fastapi",
            "--hidden-import=uvicorn",
            "--hidden-import=sqlalchemy",
            "--hidden-import=cmd2",
            "--hidden-import=rich",
            "--hidden-import=requests",
            "--hidden-import=feedparser",
            "--hidden-import=apscheduler",
            "--hidden-import=pyyaml",
            "--hidden-import=beautifulsoup4",
            server_entry_point
        ]
        
        print("执行命令: {}".format(' '.join(cmd)))
        print("注意: 实际打包过程可能需要几分钟时间...")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)  # 10分钟超时
        if result.returncode != 0:
            print("服务端打包失败: {}".format(result.stderr))
            print("stdout: {}".format(result.stdout))
            return False
        
        print("服务端打包成功")
        return True
    except subprocess.TimeoutExpired:
        print("服务端打包超时，请检查是否有错误或手动完成打包过程")
        return False
    finally:
        # 清理临时文件
        if os.path.exists(server_entry_point):
            os.remove(server_entry_point)
        spec_file = server_entry_point.replace('.py', '.spec')
        if os.path.exists(spec_file):
            os.remove(spec_file)


def build_client(output_dir="dist"):
    """打包客户端程序"""
    print("开始打包客户端...")
    
    # 创建一个临时的客户端入口脚本
    client_entry_point = "client_standalone.py"
    with open(client_entry_point, "w", encoding="utf-8") as f:
        f.write('''#!/usr/bin/env python3
"""
AnimeLoader 客户端独立运行入口
"""
import sys
import os

# 添加项目根目录到 Python 路径
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# 导入并运行客户端主函数
from client.main import main

if __name__ == "__main__":
    main()
''')
    
    try:
        # 使用 PyInstaller 打包客户端
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--name", "animeloader-client",
            "--onefile",
            "--distpath", output_dir,
            "--clean",
            "--hidden-import=cmd2",
            "--hidden-import=rich",
            "--hidden-import=requests",
            "--hidden-import=pyyaml",
            client_entry_point
        ]
        
        print("执行命令: {}".format(' '.join(cmd)))
        print("注意: 实际打包过程可能需要几分钟时间...")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)  # 10分钟超时
        if result.returncode != 0:
            print("客户端打包失败: {}".format(result.stderr))
            print("stdout: {}".format(result.stdout))
            return False
        
        print("客户端打包成功")
        return True
    except subprocess.TimeoutExpired:
        print("客户端打包超时，请检查是否有错误或手动完成打包过程")
        return False
    finally:
        # 清理临时文件
        if os.path.exists(client_entry_point):
            os.remove(client_entry_point)
        spec_file = client_entry_point.replace('.py', '.spec')
        if os.path.exists(spec_file):
            os.remove(spec_file)


def full_build():
    """完整构建两个二进制文件"""
    print("开始完整构建过程...")
    print("=" * 40)
    
    # 确保当前目录是项目根目录
    project_root = Path(__file__).parent.resolve()
    os.chdir(project_root)
    print(f"项目根目录: {project_root}")
    
    # 创建输出目录
    output_dir = "dist"
    os.makedirs(output_dir, exist_ok=True)
    
    # 安装 PyInstaller
    if not install_pyinstaller():
        print("无法安装 PyInstaller，退出")
        return False
    
    # 打包服务端
    if not build_server(output_dir):
        print("服务端打包失败，退出")
        return False
    
    # 打包客户端
    if not build_client(output_dir):
        print("客户端打包失败，退出")
        return False
    
    print("=" * 40)
    print("完整构建完成！")
    print("生成的二进制文件位于: {}".format(os.path.abspath(output_dir)))
    print("- animeloader-server (服务端可执行文件)")
    print("- animeloader-client (客户端可执行文件)")
    print()
    print("使用方法:")
    print("  启动服务端: ./dist/animeloader-server")
    print("  启动客户端: ./dist/animeloader-client")
    
    return True


def test_build():
    """测试打包配置是否正确"""
    print("测试打包配置...")
    
    # 确保当前目录是项目根目录
    project_root = Path(__file__).parent.resolve()
    os.chdir(project_root)
    print(f"项目根目录: {project_root}")
    
    # 检查服务器主模块是否存在
    try:
        import server.main
        print("✓ 服务器主模块导入成功")
    except ImportError as e:
        print("✗ 服务器主模块导入失败: {}".format(e))
        return False
    
    # 检查客户端主模块是否存在
    try:
        import client.main
        print("✓ 客户端主模块导入成功")
    except ImportError as e:
        print("✗ 客户端主模块导入失败: {}".format(e))
        return False
    
    print("✓ 所有模块依赖检查通过")
    print("✓ 打包环境配置完整")
    return True


def main():
    """主函数"""
    print("AnimeLoader 二进制打包工具")
    print("=" * 40)
    
    # 检查是否有参数
    if len(sys.argv) > 1:
        if sys.argv[1] == "full":
            print("执行完整构建过程...")
            full_build()
        elif sys.argv[1] == "test":
            print("执行配置测试...")
            test_build()
        else:
            print("用法:")
            print("  python build.py          # 显示此帮助信息")
            print("  python build.py test     # 测试打包配置")
            print("  python build.py full     # 执行完整构建")
    else:
        print("使用方法:")
        print("  python build.py test       # 测试打包配置是否正确")
        print("  python build.py full       # 执行完整构建过程")
        print()
        print("注意: 完整构建过程可能需要较长时间")


if __name__ == "__main__":
    main()