import sys
import os
import argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cmd2
from rich.console import Console
from rich.theme import Theme
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from client.api import APIClient
from client.utils import config
from client.commands.anime_commands import AnimeCommands


class AnimeLoaderCLI(cmd2.Cmd):
    intro = 'AnimeLoader CLI - 动画加载器命令行工具\n输入 help 或 ? 查看可用命令。\n'
    prompt = 'Animeloader > '
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = config

        # 显式设置提示符
        self.prompt = 'Animeloader > '

        # 初始化 APIClient
        server_url = self.config.get('server.url', 'http://127.0.0.1:8000')
        timeout = self.config.get('server.timeout', 30)
        api_key = self.config.get('server.api_key', '')
        self.api_client = APIClient(base_url=server_url, timeout=timeout, api_key=api_key)

        # 初始化 Rich Console
        self.console = Console(theme=self._get_theme())

        # 配置 cmd2 选项
        self.allow_cli_args = self.config.get('ui.cmd2.allow_cli_args', True)
        self.shortcuts = self.config.get('ui.cmd2.shortcuts', True)

        # 初始化命令处理器
        self.anime_commands = AnimeCommands(self.api_client, self.console, self.config)
    
    def _get_theme(self):
        theme_name = self.config.get('display.theme', 'auto')
        colors = self.config.get('display.colors', {})
        
        return Theme({
            'success': colors.get('success', 'green'),
            'error': colors.get('error', 'red'),
            'warning': colors.get('warning', 'yellow'),
            'info': colors.get('info', 'blue'),
            'download_speed': colors.get('download_speed', 'cyan'),
            'upload_speed': colors.get('upload_speed', 'magenta'),
        })
    
    def _print_success(self, message: str):
        emoji = "✅ " if self.config.get('ui.emoji', True) else ""
        self.console.print(f"{emoji}{message}", style="success")
    
    def _print_error(self, message: str):
        emoji = "❌ " if self.config.get('ui.emoji', True) else ""
        self.console.print(f"{emoji}{message}", style="error")
    
    def _print_warning(self, message: str):
        emoji = "⚠️  " if self.config.get('ui.emoji', True) else ""
        self.console.print(f"{emoji}{message}", style="warning")
    
    def _print_info(self, message: str):
        emoji = "ℹ️  " if self.config.get('ui.emoji', True) else ""
        self.console.print(f"{emoji}{message}", style="info")
    
    def do_anime(self, args):
        """动画相关命令

        子命令:
          add         添加动画
          list        列出所有动画
          show        显示动画详情
          smart-add   智能添加动画（从链接自动解析）
        """
        if not args:
            self._print_info("请指定子命令: add, list, show, smart-add")
            self._print_info("使用 'anime --help' 查看详细帮助")
            return

        # 解析子命令
        parts = args.split(maxsplit=1)
        subcommand = parts[0]
        subcommand_args = parts[1] if len(parts) > 1 else ""

        if subcommand == 'add':
            self.anime_commands.add(subcommand_args)
        elif subcommand == 'list':
            self.anime_commands.list(subcommand_args)
        elif subcommand == 'show':
            self.anime_commands.show(subcommand_args)
        elif subcommand == 'smart-add':
            self.anime_commands.smart_add(subcommand_args)
        elif subcommand in ['--help', '-h', 'help']:
            self.anime_commands.help()
        else:
            self._print_error(f"未知的子命令: {subcommand}")
            self._print_info("可用子命令: add, list, show, smart-add")
    
    
    
    def do_rss(self, args):
        """RSS源相关命令"""
        self._print_info("RSS命令尚未实现")
    
    def do_link(self, args):
        """链接相关命令"""
        self._print_info("链接命令尚未实现")
    
    def do_downloader(self, args):
        """下载器相关命令"""
        self._print_info("下载器命令尚未实现")
    
    def do_download(self, args):
        """下载相关命令"""
        self._print_info("下载命令尚未实现")
    
    def do_status(self, args):
        """状态查询命令"""
        self._print_info("状态命令尚未实现")
    
    def do_config(self, args):
        """查看当前配置"""
        config_table = Table(title="当前配置")
        config_table.add_column("配置项", style="cyan")
        config_table.add_column("值", style="green")
        
        config_table.add_row("服务端URL", self.config.get('server.url'))
        config_table.add_row("请求超时", str(self.config.get('server.timeout')))
        config_table.add_row("主题", self.config.get('display.theme'))
        config_table.add_row("使用 Rich", str(self.config.get('ui.use_rich')))
        config_table.add_row("使用 cmd2", str(self.config.get('ui.use_cmd2')))
        
        self.console.print(config_table)
    
    def do_exit(self, args):
        """退出程序"""
        self._print_success("再见！")
        return True
    
    def do_quit(self, args):
        """退出程序"""
        return self.do_exit(args)
    
    def do_clear(self, args):
        """清屏"""
        self.console.clear()


def parse_arguments():
    parser = argparse.ArgumentParser(description='AnimeLoader CLI - 动画加载器命令行工具')
    parser.add_argument(
        '--config',
        type=str,
        help='指定配置文件路径'
    )
    parser.add_argument(
        '--version',
        action='version',
        version='AnimeLoader CLI 0.1.0'
    )
    return parser.parse_args()


def main():
    # 在 cmd2 初始化之前先解析 --config 参数
    # 保存原始 sys.argv
    original_argv = sys.argv.copy()
    
    # 解析命令行参数（只关心 --config）
    args = parse_arguments()
    
    # 如果指定了配置文件，重新加载配置
    if args.config:
        from client.utils.config import ClientConfig
        global config
        config = ClientConfig(args.config)
    
    # 清理 sys.argv，防止 cmd2 解析我们的参数
    # 只保留脚本名称，移除所有其他参数
    sys.argv = [sys.argv[0]]
    
    # 使用 Rich 显示欢迎信息
    console = Console()
    
    welcome_text = Text()
    welcome_text.append("🎬 ", style="bold magenta")
    welcome_text.append("AnimeLoader CLI", style="bold blue")
    welcome_text.append(" - 动画加载器命令行工具", style="bold white")
    
    welcome_panel = Panel(
        welcome_text,
        border_style="blue",
        padding=(1, 2)
    )
    
    console.print(welcome_panel)
    
    # 显示配置信息
    server_url = config.get('server.url', 'http://127.0.0.1:8000')
    console.print(f"📡 连接到服务端: [cyan]{server_url}[/cyan]")
    
    if not config.get('ui.use_cmd2', True):
        console.print("[yellow]警告: cmd2 已禁用，交互式 Shell 不可用[/yellow]")
        return
    
    console.print()
    console.print("[dim]提示: 服务端API尚未实现，当前仅提供CLI框架[/dim]")
    console.print("[dim]输入 'help' 或 '?' 查看可用命令[/dim]")
    console.print()
    
    try:
        cli = AnimeLoaderCLI()
        cli.cmdloop()
    except KeyboardInterrupt:
        console.print("\n[yellow]程序已中断[/yellow]")
    except Exception as e:
        console.print(f"[red]发生错误: {e}[/red]")
        import traceback
        traceback.print_exc()
    finally:
        # 恢复原始 sys.argv
        sys.argv = original_argv


if __name__ == '__main__':
    main()