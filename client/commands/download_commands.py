import argparse
import shlex
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn


class DownloadCommands:
    """下载相关命令实现"""
    
    def __init__(self, api_client, console, config):
        self.api_client = api_client
        self.console = console
        self.config = config
    
    def start(self, args):
        """开始下载"""
        parser = argparse.ArgumentParser(prog='download start', add_help=False)
        parser.add_argument('--link-id', type=int, required=True, help='链接ID')
        parser.add_argument('--downloader-id', type=int, help='下载器ID（可选，不指定则使用默认下载器）')
        parser.add_argument('-h', '--help', action='store_true', help='显示帮助')
        
        try:
            parsed = parser.parse_args(shlex.split(args))
            if parsed.help:
                parser.print_help()
                return
            
            # 构建请求数据
            data = {'link_id': parsed.link_id}
            if parsed.downloader_id:
                data['downloader_id'] = parsed.downloader_id
            
            self.console.print(f"正在创建下载任务...")
            
            # 调用API创建下载任务
            response = self.api_client.post('/api/downloads', json_data=data)
            
            if 'error' in response:
                self._print_error(f"创建下载任务失败: {response['error']}")
                return
            
            task = response
            self._print_success(f"下载任务创建成功 (ID: {task['id']})")
            
            # 自动开始下载
            start_response = self.api_client.post(f'/api/downloads/{task["id"]}/start')
            
            if 'error' in start_response:
                self._print_warning(f"下载任务创建成功，但启动失败: {start_response['error']}")
            else:
                self._print_success(f"下载已开始")
                
        except SystemExit:
            pass
        except Exception as e:
            self._print_error(f"参数错误: {e}")
    
    def list(self, args):
        """列出下载任务"""
        parser = argparse.ArgumentParser(prog='download list', add_help=False)
        parser.add_argument('--status', help='状态过滤 (pending, downloading, completed, failed, seeding)')
        parser.add_argument('--rss-source-id', type=int, help='RSS源ID')
        parser.add_argument('--link-id', type=int, help='链接ID')
        parser.add_argument('--page', type=int, default=1, help='页码（从1开始）')
        parser.add_argument('--size', type=int, default=20, help='每页记录数')
        parser.add_argument('-h', '--help', action='store_true', help='显示帮助')
        
        try:
            parsed = parser.parse_args(shlex.split(args))
            if parsed.help:
                parser.print_help()
                return
            
            # 构建查询参数
            params = {
                'page': parsed.page,
                'size': parsed.size
            }
            
            if parsed.status:
                params['status'] = parsed.status
            if parsed.rss_source_id:
                params['rss_source_id'] = parsed.rss_source_id
            if parsed.link_id:
                params['link_id'] = parsed.link_id
            
            # 调用API获取下载任务列表
            response = self.api_client.get('/api/downloads', params=params)
            
            if 'error' in response:
                self._print_error(f"获取下载任务列表失败: {response['error']}")
                return
            
            total = response.get('total', 0)
            items = response.get('items', [])
            
            if not items:
                self._print_info("没有找到下载任务")
                return
            
            # 计算总页数
            total_pages = (total + parsed.size - 1) // parsed.size if total > 0 else 1
            
            # 显示下载任务列表
            table = Table(title=f"下载任务列表 (共 {total} 条，第 {parsed.page}/{total_pages} 页)")
            table.add_column("ID", style="cyan", width=6)
            table.add_column("状态", style="magenta", width=10)
            table.add_column("进度", style="green", width=8)
            table.add_column("下载速度", style="yellow", width=12)
            table.add_column("文件大小", style="blue", width=12)
            table.add_column("已下载", style="red", width=12)
            table.add_column("创建时间", style="dim", width=19)
            
            for task in items:
                progress = task.get('progress', 0)
                progress_str = f"{progress:.1f}%"
                
                download_speed = task.get('download_speed', 0)
                speed_str = self._format_speed(download_speed)
                
                file_size = task.get('file_size', 0)
                size_str = self._format_size(file_size)
                
                downloaded_size = task.get('downloaded_size', 0)
                downloaded_str = self._format_size(downloaded_size)
                
                table.add_row(
                    str(task['id']),
                    task.get('status', 'N/A'),
                    progress_str,
                    speed_str,
                    size_str,
                    downloaded_str,
                    task.get('created_at', 'N/A')[:19]
                )
            
            self.console.print(table)
            
            if total > parsed.size:
                self._print_info(f"显示第 {parsed.page} 页，共 {total_pages} 页，每页 {parsed.size} 条")
                
        except SystemExit:
            pass
        except Exception as e:
            self._print_error(f"参数错误: {e}")
    
    def pause(self, args):
        """暂停下载"""
        parser = argparse.ArgumentParser(prog='download pause', add_help=False)
        parser.add_argument('--id', type=int, required=True, help='下载任务ID')
        parser.add_argument('-h', '--help', action='store_true', help='显示帮助')
        
        try:
            parsed = parser.parse_args(shlex.split(args))
            if parsed.help:
                parser.print_help()
                return
            
            # 调用API暂停下载
            response = self.api_client.post(f'/api/downloads/{parsed.id}/pause')
            
            if 'error' in response:
                self._print_error(f"暂停下载失败: {response['error']}")
                return
            
            self._print_success(f"下载已暂停 (ID: {parsed.id})")
                
        except SystemExit:
            pass
        except Exception as e:
            self._print_error(f"参数错误: {e}")
    
    def resume(self, args):
        """恢复下载"""
        parser = argparse.ArgumentParser(prog='download resume', add_help=False)
        parser.add_argument('--id', type=int, required=True, help='下载任务ID')
        parser.add_argument('-h', '--help', action='store_true', help='显示帮助')
        
        try:
            parsed = parser.parse_args(shlex.split(args))
            if parsed.help:
                parser.print_help()
                return
            
            # 调用API恢复下载
            response = self.api_client.post(f'/api/downloads/{parsed.id}/resume')
            
            if 'error' in response:
                self._print_error(f"恢复下载失败: {response['error']}")
                return
            
            self._print_success(f"下载已恢复 (ID: {parsed.id})")
                
        except SystemExit:
            pass
        except Exception as e:
            self._print_error(f"参数错误: {e}")
    
    def cancel(self, args):
        """取消下载"""
        parser = argparse.ArgumentParser(prog='download cancel', add_help=False)
        parser.add_argument('--id', type=int, required=True, help='下载任务ID')
        parser.add_argument('-h', '--help', action='store_true', help='显示帮助')
        
        try:
            parsed = parser.parse_args(shlex.split(args))
            if parsed.help:
                parser.print_help()
                return
            
            # 调用API取消下载
            response = self.api_client.post(f'/api/downloads/{parsed.id}/cancel')
            
            if 'error' in response:
                self._print_error(f"取消下载失败: {response['error']}")
                return
            
            self._print_success(f"下载已取消 (ID: {parsed.id})")
                
        except SystemExit:
            pass
        except Exception as e:
            self._print_error(f"参数错误: {e}")
    
    def status(self, args):
        """查看下载状态"""
        parser = argparse.ArgumentParser(prog='download status', add_help=False)
        parser.add_argument('--id', type=int, required=True, help='下载任务ID')
        parser.add_argument('-h', '--help', action='store_true', help='显示帮助')
        
        try:
            parsed = parser.parse_args(shlex.split(args))
            if parsed.help:
                parser.print_help()
                return
            
            # 调用API获取下载任务状态
            response = self.api_client.get(f'/api/downloads/{parsed.id}')
            
            if 'error' in response:
                self._print_error(f"获取下载状态失败: {response['error']}")
                return
            
            task = response
            
            # 显示下载状态
            table = Table(title=f"下载任务状态 (ID: {task['id']})")
            table.add_column("属性", style="cyan")
            table.add_column("值", style="green")
            
            table.add_row("状态", task.get('status', 'N/A'))
            
            progress = task.get('progress', 0)
            table.add_row("进度", f"{progress:.2f}%")
            
            download_speed = task.get('download_speed', 0)
            table.add_row("下载速度", self._format_speed(download_speed))
            
            upload_speed = task.get('upload_speed', 0)
            table.add_row("上传速度", self._format_speed(upload_speed))
            
            file_size = task.get('file_size', 0)
            table.add_row("文件大小", self._format_size(file_size))
            
            downloaded_size = task.get('downloaded_size', 0)
            table.add_row("已下载", self._format_size(downloaded_size))
            
            table.add_row("文件路径", task.get('file_path', 'N/A'))
            table.add_row("错误信息", task.get('error_message', 'N/A') or '无')
            table.add_row("重试次数", str(task.get('retry_count', 0)))
            table.add_row("创建时间", task.get('created_at', 'N/A'))
            table.add_row("开始时间", task.get('started_at', 'N/A'))
            table.add_row("完成时间", task.get('completed_at', 'N/A'))
            
            self.console.print(table)
            
            # 显示进度条
            if task.get('status') == 'downloading':
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    BarColumn(),
                    TaskProgressColumn(),
                    TimeElapsedColumn(),
                    console=self.console
                ) as progress:
                    task_progress = progress.add_task(
                        f"[cyan]下载中...",
                        total=100,
                        completed=progress
                    )
                    progress.update(task_progress, completed=progress)
                
        except SystemExit:
            pass
        except Exception as e:
            self._print_error(f"参数错误: {e}")
    
    def sync(self, args):
        """同步下载状态"""
        parser = argparse.ArgumentParser(prog='download sync', add_help=False)
        parser.add_argument('--id', type=int, required=True, help='下载任务ID')
        parser.add_argument('-h', '--help', action='store_true', help='显示帮助')
        
        try:
            parsed = parser.parse_args(shlex.split(args))
            if parsed.help:
                parser.print_help()
                return
            
            self.console.print(f"正在同步下载状态 (ID: {parsed.id})...")
            
            # 调用API同步下载状态
            response = self.api_client.post(f'/api/downloads/{parsed.id}/sync')
            
            if 'error' in response:
                self._print_error(f"同步下载状态失败: {response['error']}")
                return
            
            task = response
            self._print_success(f"下载状态同步成功")
            self.console.print(f"状态: {task.get('status', 'N/A')}")
            self.console.print(f"进度: {task.get('progress', 0):.2f}%")
            
        except SystemExit:
            pass
        except Exception as e:
            self._print_error(f"参数错误: {e}")
    
    def active(self, args):
        """查看活跃的下载任务"""
        parser = argparse.ArgumentParser(prog='download active', add_help=False)
        parser.add_argument('-h', '--help', action='store_true', help='显示帮助')
        
        try:
            parsed = parser.parse_args(shlex.split(args))
            if parsed.help:
                parser.print_help()
                return
            
            # 调用API获取活跃的下载任务
            response = self.api_client.get('/api/downloads/active')
            
            if 'error' in response:
                self._print_error(f"获取活跃下载任务失败: {response['error']}")
                return
            
            tasks = response if isinstance(response, list) else []
            
            if not tasks:
                self._print_info("当前没有活跃的下载任务")
                return
            
            # 显示活跃下载任务
            table = Table(title=f"活跃下载任务 ({len(tasks)} 个)")
            table.add_column("ID", style="cyan", width=6)
            table.add_column("状态", style="magenta", width=12)
            table.add_column("进度", style="green", width=8)
            table.add_column("下载速度", style="yellow", width=12)
            table.add_column("已下载", style="blue", width=12)
            
            for task in tasks:
                progress = task.get('progress', 0)
                progress_str = f"{progress:.1f}%"
                
                download_speed = task.get('download_speed', 0)
                speed_str = self._format_speed(download_speed)
                
                downloaded_size = task.get('downloaded_size', 0)
                downloaded_str = self._format_size(downloaded_size)
                
                table.add_row(
                    str(task['id']),
                    task.get('status', 'N/A'),
                    progress_str,
                    speed_str,
                    downloaded_str
                )
            
            self.console.print(table)
                
        except SystemExit:
            pass
        except Exception as e:
            self._print_error(f"参数错误: {e}")
    
    def help(self):
        """显示 download 命令的帮助信息"""
        help_text = """
下载相关命令

用法: download <子命令> [选项]

子命令:
  start   开始下载
  list    列出下载任务
  pause   暂停下载
  resume  恢复下载
  cancel  取消下载
  status  查看下载状态
  sync    同步下载状态
  active  查看活跃的下载任务

使用 'download <子命令> --help' 查看子命令的详细帮助
        """
        self.console.print(help_text)
    
    def _format_size(self, size_bytes: int) -> str:
        """格式化文件大小"""
        if size_bytes == 0:
            return "N/A"
        
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        
        return f"{size_bytes:.2f} PB"
    
    def _format_speed(self, speed_bytes: float) -> str:
        """格式化速度"""
        if speed_bytes == 0:
            return "N/A"
        
        for unit in ['B/s', 'KB/s', 'MB/s', 'GB/s', 'TB/s']:
            if speed_bytes < 1024.0:
                return f"{speed_bytes:.2f} {unit}"
            speed_bytes /= 1024.0
        
        return f"{speed_bytes:.2f} PB/s"
    
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