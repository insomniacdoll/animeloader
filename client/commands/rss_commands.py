import argparse
import shlex
from rich.console import Console
from rich.table import Table


class RSSCommands:
    """RSS源相关命令实现"""
    
    def __init__(self, api_client, console, config):
        self.api_client = api_client
        self.console = console
        self.config = config
    
    def add(self, args):
        """添加RSS源"""
        parser = argparse.ArgumentParser(prog='rss add', add_help=False)
        parser.add_argument('--anime-id', type=int, required=True, help='动画ID')
        parser.add_argument('--name', required=True, help='RSS源名称')
        parser.add_argument('--url', required=True, help='RSS订阅链接')
        parser.add_argument('--quality', help='画质 (1080p, 720p, 480p)')
        parser.add_argument('--auto-download', action='store_true', help='是否自动下载')
        parser.add_argument('-h', '--help', action='store_true', help='显示帮助')
        
        try:
            parsed = parser.parse_args(shlex.split(args))
            if parsed.help:
                parser.print_help()
                return
            
            # 构建请求数据
            data = {
                'anime_id': parsed.anime_id,
                'name': parsed.name,
                'url': parsed.url,
                'is_active': True,
                'auto_download': parsed.auto_download
            }
            
            if parsed.quality:
                data['quality'] = parsed.quality
            
            # 调用API创建RSS源
            response = self.api_client.post('/api/rss-sources', json_data=data)
            
            if 'error' in response:
                self._print_error(f"添加RSS源失败: {response['error']}")
                return
            
            rss = response
            self._print_success(f"RSS源添加成功: {rss['name']}")
            self.console.print(f"ID: {rss['id']}")
            self.console.print(f"URL: {rss['url']}")
            self.console.print(f"画质: {rss.get('quality', 'N/A')}")
            self.console.print(f"自动下载: {'是' if rss.get('auto_download') else '否'}")
                
        except SystemExit:
            pass
        except Exception as e:
            self._print_error(f"参数错误: {e}")
    
    def list(self, args):
        """列出RSS源"""
        parser = argparse.ArgumentParser(prog='rss list', add_help=False)
        parser.add_argument('--anime-id', type=int, help='动画ID（过滤特定动画的RSS源）')
        parser.add_argument('-h', '--help', action='store_true', help='显示帮助')
        
        try:
            parsed = parser.parse_args(shlex.split(args))
            if parsed.help:
                parser.print_help()
                return
            
            # 调用API获取RSS源列表
            if parsed.anime_id:
                response = self.api_client.get(f'/api/anime/{parsed.anime_id}/rss-sources')
            else:
                # 获取所有RSS源（需要遍历所有动画）
                anime_response = self.api_client.get('/api/anime', params={'page': 1, 'size': 1000})
                if 'error' in anime_response:
                    self._print_error(f"获取动画列表失败: {anime_response['error']}")
                    return
                
                animes = anime_response.get('items', [])
                all_rss_sources = []
                
                for anime in animes:
                    rss_response = self.api_client.get(f'/api/anime/{anime["id"]}/rss-sources')
                    if 'error' not in rss_response:
                        for rss in rss_response:
                            rss['anime_title'] = anime['title']
                            all_rss_sources.append(rss)
                
                response = all_rss_sources
            
            if 'error' in response:
                self._print_error(f"获取RSS源列表失败: {response['error']}")
                return
            
            rss_sources = response if isinstance(response, list) else []
            
            if not rss_sources:
                self._print_info("没有找到RSS源")
                return
            
            # 显示RSS源列表
            table = Table(title=f"RSS源列表 (共 {len(rss_sources)} 条)")
            table.add_column("ID", style="cyan", width=6)
            table.add_column("名称", style="magenta")
            table.add_column("动画", style="green")
            table.add_column("URL", style="blue")
            table.add_column("画质", style="yellow", width=8)
            table.add_column("状态", style="red", width=6)
            table.add_column("自动下载", style="cyan", width=8)
            
            for rss in rss_sources:
                table.add_row(
                    str(rss['id']),
                    rss['name'],
                    rss.get('anime_title', 'N/A'),
                    rss['url'][:50] + '...' if len(rss['url']) > 50 else rss['url'],
                    rss.get('quality', 'N/A'),
                    "激活" if rss.get('is_active') else "停用",
                    "是" if rss.get('auto_download') else "否"
                )
            
            self.console.print(table)
                
        except SystemExit:
            pass
        except Exception as e:
            self._print_error(f"参数错误: {e}")
    
    def show(self, args):
        """显示RSS源详情"""
        parser = argparse.ArgumentParser(prog='rss show', add_help=False)
        parser.add_argument('--id', type=int, required=True, help='RSS源ID')
        parser.add_argument('-h', '--help', action='store_true', help='显示帮助')
        
        try:
            parsed = parser.parse_args(shlex.split(args))
            if parsed.help:
                parser.print_help()
                return
            
            # 调用API获取RSS源详情
            response = self.api_client.get(f'/api/rss-sources/{parsed.id}')
            
            if 'error' in response:
                self._print_error(f"获取RSS源详情失败: {response['error']}")
                return
            
            rss = response
            
            # 显示RSS源详情
            table = Table(title=f"RSS源详情: {rss['name']}")
            table.add_column("属性", style="cyan")
            table.add_column("值", style="green")
            
            table.add_row("ID", str(rss['id']))
            table.add_row("名称", rss['name'])
            table.add_row("动画ID", str(rss.get('anime_id', 'N/A')))
            table.add_row("URL", rss['url'])
            table.add_row("画质", rss.get('quality', 'N/A'))
            table.add_row("状态", "激活" if rss.get('is_active') else "停用")
            table.add_row("自动下载", "是" if rss.get('auto_download') else "否")
            table.add_row("最后检查时间", rss.get('last_checked_at', 'N/A'))
            table.add_row("创建时间", rss.get('created_at', 'N/A'))
            table.add_row("更新时间", rss.get('updated_at', 'N/A'))
            
            self.console.print(table)
            
        except SystemExit:
            pass
        except Exception as e:
            self._print_error(f"参数错误: {e}")
    
    def update(self, args):
        """更新RSS源"""
        parser = argparse.ArgumentParser(prog='rss update', add_help=False)
        parser.add_argument('--id', type=int, required=True, help='RSS源ID')
        parser.add_argument('--name', help='RSS源名称')
        parser.add_argument('--url', help='RSS订阅链接')
        parser.add_argument('--quality', help='画质 (1080p, 720p, 480p)')
        parser.add_argument('--is-active', type=bool, help='是否激活')
        parser.add_argument('--auto-download', type=bool, help='是否自动下载')
        parser.add_argument('-h', '--help', action='store_true', help='显示帮助')
        
        try:
            parsed = parser.parse_args(shlex.split(args))
            if parsed.help:
                parser.print_help()
                return
            
            # 构建请求数据
            data = {}
            
            if parsed.name:
                data['name'] = parsed.name
            if parsed.url:
                data['url'] = parsed.url
            if parsed.quality:
                data['quality'] = parsed.quality
            if parsed.is_active is not None:
                data['is_active'] = parsed.is_active
            if parsed.auto_download is not None:
                data['auto_download'] = parsed.auto_download
            
            if not data:
                self._print_warning("没有提供任何更新参数")
                return
            
            # 调用API更新RSS源
            response = self.api_client.put(f'/api/rss-sources/{parsed.id}', json_data=data)
            
            if 'error' in response:
                self._print_error(f"更新RSS源失败: {response['error']}")
                return
            
            rss = response
            self._print_success(f"RSS源更新成功: {rss['name']}")
                
        except SystemExit:
            pass
        except Exception as e:
            self._print_error(f"参数错误: {e}")
    
    def remove(self, args):
        """删除RSS源"""
        parser = argparse.ArgumentParser(prog='rss remove', add_help=False)
        parser.add_argument('--id', type=int, required=True, help='RSS源ID')
        parser.add_argument('-h', '--help', action='store_true', help='显示帮助')
        
        try:
            parsed = parser.parse_args(shlex.split(args))
            if parsed.help:
                parser.print_help()
                return
            
            # 调用API删除RSS源
            response = self.api_client.delete(f'/api/rss-sources/{parsed.id}')
            
            if 'error' in response:
                self._print_error(f"删除RSS源失败: {response['error']}")
                return
            
            self._print_success(f"RSS源删除成功 (ID: {parsed.id})")
                
        except SystemExit:
            pass
        except Exception as e:
            self._print_error(f"参数错误: {e}")
    
    def check(self, args):
        """手动检查RSS源新链接"""
        parser = argparse.ArgumentParser(prog='rss check', add_help=False)
        parser.add_argument('--id', type=int, required=True, help='RSS源ID')
        parser.add_argument('--auto-download', action='store_true', help='是否自动下载新链接')
        parser.add_argument('-h', '--help', action='store_true', help='显示帮助')
        
        try:
            parsed = parser.parse_args(shlex.split(args))
            if parsed.help:
                parser.print_help()
                return
            
            self.console.print(f"正在检查RSS源 (ID: {parsed.id})...")
            
            # 调用API检查RSS源
            response = self.api_client.post(f'/api/rss-sources/{parsed.id}/check', json_data={
                'auto_download': parsed.auto_download
            })
            
            if 'error' in response:
                self._print_error(f"检查RSS源失败: {response['error']}")
                return
            
            result = response
            new_links = result.get('new_links', 0)
            downloaded = result.get('downloaded', 0)
            
            self._print_success(f"检查完成: 发现 {new_links} 个新链接")
            if downloaded > 0:
                self._print_success(f"已自动下载 {downloaded} 个链接")
                
        except SystemExit:
            pass
        except Exception as e:
            self._print_error(f"参数错误: {e}")
    
    def help(self):
        """显示 rss 命令的帮助信息"""
        help_text = """
RSS源相关命令

用法: rss <子命令> [选项]

子命令:
  add         添加RSS源
  list        列出RSS源
  show        显示RSS源详情
  update      更新RSS源
  remove      删除RSS源
  check       手动检查RSS源新链接

使用 'rss <子命令> --help' 查看子命令的详细帮助
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