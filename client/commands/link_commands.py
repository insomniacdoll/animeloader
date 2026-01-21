import argparse
import shlex
from rich.console import Console
from rich.table import Table


class LinkCommands:
    """链接相关命令实现"""
    
    def __init__(self, api_client, console, config):
        self.api_client = api_client
        self.console = console
        self.config = config
    
    def list(self, args):
        """列出链接"""
        parser = argparse.ArgumentParser(prog='link list', add_help=False)
        parser.add_argument('--rss-source-id', type=int, help='RSS源ID（过滤特定RSS源的链接）')
        parser.add_argument('--type', help='链接类型过滤 (magnet, ed2k, http, ftp)')
        parser.add_argument('--downloaded', type=bool, help='是否已下载')
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
            
            if parsed.rss_source_id:
                params['rss_source_id'] = parsed.rss_source_id
            if parsed.type:
                params['link_type'] = parsed.type
            if parsed.downloaded is not None:
                params['is_downloaded'] = parsed.downloaded
            
            # 调用API获取链接列表
            response = self.api_client.get('/api/links', params=params)
            
            if 'error' in response:
                self._print_error(f"获取链接列表失败: {response['error']}")
                return
            
            total = response.get('total', 0)
            items = response.get('items', [])
            
            if not items:
                self._print_info("没有找到链接")
                return
            
            # 计算总页数
            total_pages = (total + parsed.size - 1) // parsed.size if total > 0 else 1
            
            # 显示链接列表
            table = Table(title=f"链接列表 (共 {total} 条，第 {parsed.page}/{total_pages} 页)")
            table.add_column("ID", style="cyan", width=6)
            table.add_column("集数", style="magenta", width=6)
            table.add_column("标题", style="green")
            table.add_column("类型", style="yellow", width=8)
            table.add_column("大小", style="blue", width=12)
            table.add_column("下载状态", style="red", width=8)
            table.add_column("可用状态", style="cyan", width=8)
            table.add_column("发布时间", style="dim", width=19)
            
            for link in items:
                file_size = link.get('file_size', 0)
                size_str = self._format_size(file_size)
                
                table.add_row(
                    str(link['id']),
                    str(link.get('episode_number', 'N/A')),
                    link.get('episode_title', 'N/A')[:30] + '...' if len(link.get('episode_title', '')) > 30 else link.get('episode_title', 'N/A'),
                    link.get('link_type', 'N/A'),
                    size_str,
                    "已下载" if link.get('is_downloaded') else "未下载",
                    "可用" if link.get('is_available') else "不可用",
                    link.get('publish_date', 'N/A')[:19] if link.get('publish_date') else 'N/A'
                )
            
            self.console.print(table)
            
            if total > parsed.size:
                self._print_info(f"显示第 {parsed.page} 页，共 {total_pages} 页，每页 {parsed.size} 条")
                
        except SystemExit:
            pass
        except Exception as e:
            self._print_error(f"参数错误: {e}")
    
    def show(self, args):
        """显示链接详情"""
        parser = argparse.ArgumentParser(prog='link show', add_help=False)
        parser.add_argument('--id', type=int, required=True, help='链接ID')
        parser.add_argument('-h', '--help', action='store_true', help='显示帮助')
        
        try:
            parsed = parser.parse_args(shlex.split(args))
            if parsed.help:
                parser.print_help()
                return
            
            # 调用API获取链接详情
            response = self.api_client.get(f'/api/links/{parsed.id}')
            
            if 'error' in response:
                self._print_error(f"获取链接详情失败: {response['error']}")
                return
            
            link = response
            
            # 显示链接详情
            table = Table(title=f"链接详情: {link.get('episode_title', 'N/A')}")
            table.add_column("属性", style="cyan")
            table.add_column("值", style="green")
            
            table.add_row("ID", str(link['id']))
            table.add_row("RSS源ID", str(link.get('rss_source_id', 'N/A')))
            table.add_row("集数", str(link.get('episode_number', 'N/A')))
            table.add_row("标题", link.get('episode_title', 'N/A'))
            table.add_row("类型", link.get('link_type', 'N/A'))
            table.add_row("URL", link['url'][:80] + '...' if len(link['url']) > 80 else link['url'])
            
            file_size = link.get('file_size', 0)
            table.add_row("文件大小", self._format_size(file_size))
            
            table.add_row("下载状态", "已下载" if link.get('is_downloaded') else "未下载")
            table.add_row("可用状态", "可用" if link.get('is_available') else "不可用")
            table.add_row("发布时间", link.get('publish_date', 'N/A'))
            table.add_row("创建时间", link.get('created_at', 'N/A'))
            table.add_row("更新时间", link.get('updated_at', 'N/A'))
            
            self.console.print(table)
            
        except SystemExit:
            pass
        except Exception as e:
            self._print_error(f"参数错误: {e}")
    
    def mark_downloaded(self, args):
        """标记链接为已下载"""
        parser = argparse.ArgumentParser(prog='link mark-downloaded', add_help=False)
        parser.add_argument('--id', type=int, required=True, help='链接ID')
        parser.add_argument('-h', '--help', action='store_true', help='显示帮助')
        
        try:
            parsed = parser.parse_args(shlex.split(args))
            if parsed.help:
                parser.print_help()
                return
            
            # 调用API标记链接为已下载
            response = self.api_client.post(f'/api/links/{parsed.id}/mark-downloaded')
            
            if 'error' in response:
                self._print_error(f"标记链接失败: {response['error']}")
                return
            
            self._print_success(f"链接已标记为已下载 (ID: {parsed.id})")
                
        except SystemExit:
            pass
        except Exception as e:
            self._print_error(f"参数错误: {e}")
    
    def help(self):
        """显示 link 命令的帮助信息"""
        help_text = """
链接相关命令

用法: link <子命令> [选项]

子命令:
  list            列出链接
  show            显示链接详情
  mark-downloaded 标记链接为已下载

使用 'link <子命令> --help' 查看子命令的详细帮助
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