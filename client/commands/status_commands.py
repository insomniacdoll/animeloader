import argparse
import shlex
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text


class StatusCommands:
    """状态查询命令实现"""
    
    def __init__(self, api_client, console, config):
        self.api_client = api_client
        self.console = console
        self.config = config
    
    def server(self, args):
        """查看服务器状态"""
        parser = argparse.ArgumentParser(prog='status server', add_help=False)
        parser.add_argument('-h', '--help', action='store_true', help='显示帮助')
        
        try:
            parsed = parser.parse_args(shlex.split(args))
            if parsed.help:
                parser.print_help()
                return
            
            self.console.print(f"正在获取服务器状态...")
            
            # 调用健康检查API
            response = self.api_client.get('/api/health')
            
            if 'error' in response:
                self._print_error(f"获取服务器状态失败: {response['error']}")
                return
            
            # 显示服务器状态
            status_text = Text()
            status_text.append("🟢 ", style="bold green")
            status_text.append("服务器运行正常", style="bold white")
            
            status_panel = Panel(
                status_text,
                border_style="green",
                padding=(1, 2)
            )
            
            self.console.print(status_panel)
            
            # 显示详细信息
            table = Table(title="服务器详细信息")
            table.add_column("属性", style="cyan")
            table.add_column("值", style="green")
            
            table.add_row("状态", response.get('status', 'N/A'))
            table.add_row("服务端URL", self.api_client.base_url)
            table.add_row("API密钥", "已配置" if self.api_client.api_key else "未配置")
            
            self.console.print(table)
            
        except SystemExit:
            pass
        except Exception as e:
            self._print_error(f"参数错误: {e}")
    
    def system(self, args):
        """查看系统信息"""
        parser = argparse.ArgumentParser(prog='status system', add_help=False)
        parser.add_argument('-h', '--help', action='store_true', help='显示帮助')
        
        try:
            parsed = parser.parse_args(shlex.split(args))
            if parsed.help:
                parser.print_help()
                return
            
            # 显示系统信息
            table = Table(title="系统信息")
            table.add_column("属性", style="cyan")
            table.add_column("值", style="green")
            
            table.add_row("客户端版本", "0.1.0")
            table.add_row("服务端URL", self.api_client.base_url)
            table.add_row("API密钥", "已配置" if self.api_client.api_key else "未配置")
            table.add_row("请求超时", f"{self.api_client.timeout} 秒")
            table.add_row("重试次数", str(self.api_client.retry_count))
            table.add_row("主题", self.config.get('display.theme', 'auto'))
            table.add_row("使用 Rich", str(self.config.get('ui.use_rich', True)))
            table.add_row("使用 cmd2", str(self.config.get('ui.use_cmd2', True)))
            table.add_row("使用 Emoji", str(self.config.get('ui.emoji', True)))
            
            self.console.print(table)
            
        except SystemExit:
            pass
        except Exception as e:
            self._print_error(f"参数错误: {e}")
    
    def scheduler(self, args):
        """查看调度器状态"""
        parser = argparse.ArgumentParser(prog='status scheduler', add_help=False)
        parser.add_argument('-h', '--help', action='store_true', help='显示帮助')
        
        try:
            parsed = parser.parse_args(shlex.split(args))
            if parsed.help:
                parser.print_help()
                return
            
            self.console.print(f"正在获取调度器状态...")
            
            # 调用API获取调度器任务
            response = self.api_client.get('/api/scheduler/jobs')
            
            if 'error' in response:
                self._print_error(f"获取调度器状态失败: {response['error']}")
                return
            
            jobs = response.get('jobs', [])
            is_running = response.get('is_running', False)
            
            # 显示调度器状态
            status_text = Text()
            if is_running:
                status_text.append("🟢 ", style="bold green")
                status_text.append("调度器运行中", style="bold white")
            else:
                status_text.append("🔴 ", style="bold red")
                status_text.append("调度器已停止", style="bold white")
            
            status_panel = Panel(
                status_text,
                border_style="green" if is_running else "red",
                padding=(1, 2)
            )
            
            self.console.print(status_panel)
            
            # 显示任务列表
            if jobs:
                table = Table(title=f"调度任务 ({len(jobs)} 个)")
                table.add_column("ID", style="cyan", width=6)
                table.add_column("名称", style="magenta")
                table.add_column("状态", style="yellow", width=8)
                table.add_column("下次执行", style="green", width=19)
                
                for job in jobs:
                    table.add_row(
                        str(job.get('id', 'N/A')),
                        job.get('name', 'N/A'),
                        job.get('status', 'N/A'),
                        job.get('next_run_time', 'N/A')[:19] if job.get('next_run_time') else 'N/A'
                    )
                
                self.console.print(table)
            else:
                self._print_info("当前没有调度任务")
            
        except SystemExit:
            pass
        except Exception as e:
            self._print_error(f"参数错误: {e}")
    
    def summary(self, args):
        """查看系统摘要"""
        parser = argparse.ArgumentParser(prog='status summary', add_help=False)
        parser.add_argument('-h', '--help', action='store_true', help='显示帮助')
        
        try:
            parsed = parser.parse_args(shlex.split(args))
            if parsed.help:
                parser.print_help()
                return
            
            self.console.print(f"正在获取系统摘要...")
            
            # 获取各种统计信息
            anime_response = self.api_client.get('/api/anime', params={'page': 1, 'size': 1})
            anime_count = anime_response.get('total', 0)
            
            downloader_response = self.api_client.get('/api/downloaders')
            downloader_count = len(downloader_response) if isinstance(downloader_response, list) else 0
            
            download_response = self.api_client.get('/api/downloads', params={'page': 1, 'size': 1})
            download_count = download_response.get('total', 0)
            
            active_download_response = self.api_client.get('/api/downloads/active')
            active_count = len(active_download_response) if isinstance(active_download_response, list) else 0
            
            scheduler_response = self.api_client.get('/api/scheduler/jobs')
            scheduler_running = scheduler_response.get('is_running', False)
            job_count = len(scheduler_response.get('jobs', []))
            
            # 显示系统摘要
            table = Table(title="系统摘要")
            table.add_column("项目", style="cyan")
            table.add_column("数量", style="green")
            table.add_column("状态", style="yellow")
            
            table.add_row("动画", str(anime_count), "")
            table.add_row("下载器", str(downloader_count), "")
            table.add_row("下载任务", str(download_count), "")
            table.add_row("活跃下载", str(active_count), "运行中" if active_count > 0 else "空闲")
            table.add_row("调度任务", str(job_count), "运行中" if scheduler_running else "已停止")
            
            self.console.print(table)
            
        except SystemExit:
            pass
        except Exception as e:
            self._print_error(f"参数错误: {e}")
    
    def help(self):
        """显示 status 命令的帮助信息"""
        help_text = """
状态查询命令

用法: status <子命令> [选项]

子命令:
  server    查看服务器状态
  system    查看系统信息
  scheduler 查看调度器状态
  summary   查看系统摘要

使用 'status <子命令> --help' 查看子命令的详细帮助
        """
        self.console.print(help_text)
    
    def _print_success(self, message: str):
        emoji = "✅ " if self.config.get('ui.emoji', True) else ""
        self.console.print(f"{emoji}{message}", style="green")
    
    def _print_error(self, message: str):
        emoji = "❌ " if self.config.get('ui.emoji', True) else ""
        self.console.print(f"{emoji}{message}", style="red")
    
    def _print_warning(self, message: str):
        emoji = "⚠️  " if self.config.get('ui.emoji', True) else ""
        self.console.print(f"{emoji}{message}", style="yellow")
    
    def _print_info(self, message: str):
        emoji = "ℹ️  " if self.config.get('ui.emoji', True) else ""
        self.console.print(f"{emoji}{message}", style="blue")