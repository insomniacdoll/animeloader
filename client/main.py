import sys
import os
import argparse
import shlex

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cmd2
from rich.console import Console
from rich.theme import Theme
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from client.api import APIClient
from client.utils import config


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
            self._anime_add(subcommand_args)
        elif subcommand == 'list':
            self._anime_list(subcommand_args)
        elif subcommand == 'show':
            self._anime_show(subcommand_args)
        elif subcommand == 'smart-add':
            self._anime_smart_add(subcommand_args)
        elif subcommand in ['--help', '-h', 'help']:
            self._anime_help()
        else:
            self._print_error(f"未知的子命令: {subcommand}")
            self._print_info("可用子命令: add, list, show, smart-add")
    
    def _anime_add(self, args):
        """添加动画"""
        parser = argparse.ArgumentParser(prog='anime add', add_help=False)
        parser.add_argument('--title', required=True, help='动画标题')
        parser.add_argument('--title-en', help='英文标题')
        parser.add_argument('--description', help='描述')
        parser.add_argument('--cover-url', help='封面URL')
        parser.add_argument('--status', default='ongoing', help='状态 (ongoing, completed)')
        parser.add_argument('--total-episodes', type=int, help='总集数')
        parser.add_argument('-h', '--help', action='store_true', help='显示帮助')
        
        try:
            parsed = parser.parse_args(shlex.split(args))
            if parsed.help:
                parser.print_help()
                return
            
            # 构建请求数据
            data = {
                'title': parsed.title,
                'status': parsed.status
            }
            
            if parsed.title_en:
                data['title_en'] = parsed.title_en
            if parsed.description:
                data['description'] = parsed.description
            if parsed.cover_url:
                data['cover_url'] = parsed.cover_url
            if parsed.total_episodes is not None:
                data['total_episodes'] = parsed.total_episodes
            
            # 调用API创建动画
            response = self.api_client.post('/api/anime', json_data=data)
            
            if 'error' in response:
                self._print_error(f"添加动画失败: {response['error']}")
                return
            
            anime = response
            self._print_success(f"动画添加成功: {anime['title']}")
            self.console.print(f"ID: {anime['id']}")
            self.console.print(f"英文标题: {anime.get('title_en', 'N/A')}")
            self.console.print(f"状态: {anime.get('status', 'N/A')}")
            if anime.get('total_episodes'):
                self.console.print(f"总集数: {anime['total_episodes']}")
                
        except SystemExit:
            pass
        except Exception as e:
            self._print_error(f"参数错误: {e}")
    
    def _anime_list(self, args):
        """列出所有动画"""
        parser = argparse.ArgumentParser(prog='anime list', add_help=False)
        parser.add_argument('--keyword', help='搜索关键词')
        parser.add_argument('--status', help='状态过滤 (ongoing, completed)')
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
            
            if parsed.keyword:
                params['search'] = parsed.keyword
            if parsed.status:
                params['status'] = parsed.status
            
            # 调用API获取动画列表
            response = self.api_client.get('/api/anime', params=params)
            
            if 'error' in response:
                self._print_error(f"获取动画列表失败: {response['error']}")
                return
            
            total = response.get('total', 0)
            items = response.get('items', [])
            
            if not items:
                self._print_info("没有找到动画")
                return
            
            # 计算总页数
            total_pages = (total + parsed.size - 1) // parsed.size if total > 0 else 1
            
            # 显示动画列表
            table = Table(title=f"动画列表 (共 {total} 条，第 {parsed.page}/{total_pages} 页)")
            table.add_column("ID", style="cyan", width=6)
            table.add_column("标题", style="magenta")
            table.add_column("英文标题", style="green")
            table.add_column("状态", style="yellow", width=10)
            table.add_column("集数", style="blue", width=8)
            table.add_column("创建时间", style="dim", width=19)
            
            for anime in items:
                table.add_row(
                    str(anime['id']),
                    anime['title'],
                    anime.get('title_en', 'N/A'),
                    anime.get('status', 'N/A'),
                    str(anime.get('total_episodes', 'N/A')),
                    anime.get('created_at', 'N/A')[:19]  # 只显示到秒
                )
            
            self.console.print(table)
            
            if total > parsed.size:
                self._print_info(f"显示第 {parsed.page} 页，共 {total_pages} 页，每页 {parsed.size} 条")
                
        except SystemExit:
            pass
        except Exception as e:
            self._print_error(f"参数错误: {e}")
    
    def _anime_show(self, args):
        """显示动画详情"""
        parser = argparse.ArgumentParser(prog='anime show', add_help=False)
        parser.add_argument('--id', type=int, required=True, help='动画ID')
        parser.add_argument('-h', '--help', action='store_true', help='显示帮助')
        
        try:
            parsed = parser.parse_args(shlex.split(args))
            if parsed.help:
                parser.print_help()
                return
            
            # 调用API获取动画详情
            response = self.api_client.get(f'/api/anime/{parsed.id}')
            
            if 'error' in response:
                self._print_error(f"获取动画详情失败: {response['error']}")
                return
            
            anime = response
            
            # 显示动画详情
            table = Table(title=f"动画详情: {anime['title']}")
            table.add_column("属性", style="cyan")
            table.add_column("值", style="green")
            
            table.add_row("ID", str(anime['id']))
            table.add_row("标题", anime['title'])
            table.add_row("英文标题", anime.get('title_en', 'N/A'))
            table.add_row("描述", anime.get('description', 'N/A') or 'N/A')
            table.add_row("封面URL", anime.get('cover_url', 'N/A') or 'N/A')
            table.add_row("状态", anime.get('status', 'N/A'))
            table.add_row("总集数", str(anime.get('total_episodes', 'N/A')))
            table.add_row("创建时间", anime.get('created_at', 'N/A'))
            table.add_row("更新时间", anime.get('updated_at', 'N/A'))
            
            self.console.print(table)
            
            # 获取RSS源列表
            rss_response = self.api_client.get(f'/api/anime/{parsed.id}/rss-sources')
            
            if 'error' not in rss_response:
                rss_sources = rss_response if isinstance(rss_response, list) else []
                
                if rss_sources:
                    rss_table = Table(title="关联的RSS源")
                    rss_table.add_column("ID", style="cyan", width=6)
                    rss_table.add_column("名称", style="magenta")
                    rss_table.add_column("URL", style="green")
                    rss_table.add_column("画质", style="yellow")
                    rss_table.add_column("自动下载", style="blue")
                    
                    for rss in rss_sources:
                        rss_table.add_row(
                            str(rss['id']),
                            rss['name'],
                            rss['url'],
                            rss.get('quality', 'N/A'),
                            "是" if rss.get('auto_download') else "否"
                        )
                    
                    self.console.print(rss_table)
                else:
                    self._print_info("该动画没有关联的RSS源")
                    
        except SystemExit:
            pass
        except Exception as e:
            self._print_error(f"参数错误: {e}")
    
    def _anime_smart_add(self, args):
        """智能添加动画（从链接自动解析）"""
        parser = argparse.ArgumentParser(prog='anime smart-add', add_help=False)
        parser.add_argument('--url', required=True, help='动画网站链接')
        parser.add_argument('--auto-add-rss', action='store_true', help='是否自动解析RSS源')
        parser.add_argument('-h', '--help', action='store_true', help='显示帮助')
        
        try:
            parsed = parser.parse_args(shlex.split(args))
            if parsed.help:
                parser.print_help()
                return
            
            self.console.print(f"正在解析链接: {parsed.url}")
            
            # 步骤1: 智能解析动画
            parse_response = self.api_client.post('/api/anime/smart-parse', json_data={'url': parsed.url})
            
            if 'error' in parse_response:
                self._print_error(f"解析失败: {parse_response['error']}")
                return
            
            site_name = parse_response.get('site_name', 'Unknown')
            anime_list = parse_response.get('results', [])
            
            if not anime_list:
                self._print_error("未能解析到动画信息")
                return
            
            self._print_success(f"成功从 {site_name} 解析到 {len(anime_list)} 个动画")
            
            # 显示解析结果
            table = Table(title="解析结果")
            table.add_column("ID", style="cyan", width=4)
            table.add_column("标题", style="magenta")
            table.add_column("英文标题", style="green")
            table.add_column("状态", style="yellow", width=10)
            table.add_column("集数", style="blue", width=6)
            
            for idx, anime in enumerate(anime_list, 1):
                table.add_row(
                    str(idx),
                    anime['title'],
                    anime.get('title_en', ''),
                    anime.get('status', ''),
                    str(anime.get('total_episodes', 0))
                )
            
            self.console.print(table)
            
            # 步骤2: 选择动画
            if len(anime_list) == 1:
                selected_index = 1
                self._print_info(f"自动选择唯一解析结果: {anime_list[0]['title']}")
            else:
                selected_index = self._prompt_select_anime(len(anime_list))
                if selected_index is None:
                    return
            
            selected_anime = anime_list[selected_index - 1]
            self._print_info(f"选择的动画: {selected_anime['title']}")
            
            # 步骤3: 检查RSS源
            rss_sources = selected_anime.get('rss_sources', [])
            
            rss_indices = []
            if rss_sources:
                rss_table = Table(title=f"找到 {len(rss_sources)} 个RSS源")
                rss_table.add_column("ID", style="cyan", width=4)
                rss_table.add_column("名称", style="magenta")
                rss_table.add_column("URL", style="green")
                rss_table.add_column("画质", style="yellow")
                rss_table.add_column("自动下载", style="blue")
                
                for idx, rss in enumerate(rss_sources, 1):
                    rss_table.add_row(
                        str(idx),
                        rss['name'],
                        rss['url'],
                        rss.get('quality', ''),
                        "是" if rss.get('auto_download') else "否"
                    )
                
                self.console.print(rss_table)
                
                # 选择RSS源
                if parsed.auto_add_rss:
                    rss_indices = list(range(1, len(rss_sources) + 1))
                    self._print_info(f"自动选择所有RSS源")
                else:
                    rss_indices = self._prompt_select_rss(len(rss_sources))
                    if rss_indices is None:
                        rss_indices = []
            
            # 步骤4: 智能添加
            self.console.print("\n正在添加动画...")
            
            add_response = self.api_client.post('/api/anime/smart-add', json_data={
                'url': parsed.url,
                'auto_add_rss': len(rss_indices) > 0,
                'anime_index': selected_index,
                'rss_indices': rss_indices
            })
            
            if 'error' in add_response:
                self._print_error(f"添加失败: {add_response['error']}")
                return
            
            anime = add_response.get('anime', {})
            self._print_success(f"动画添加成功: {anime.get('title', 'N/A')}")
            self.console.print(f"ID: {anime.get('id', 'N/A')}")
            
            added_rss_sources = add_response.get('rss_sources', [])
            if added_rss_sources:
                self._print_success(f"成功添加 {len(added_rss_sources)} 个RSS源:")
                for rss in added_rss_sources:
                    self.console.print(f"  - {rss.get('name', 'N/A')} (ID: {rss.get('id', 'N/A')})")
            else:
                self._print_info("未添加RSS源")
                
        except SystemExit:
            pass
        except Exception as e:
            self._print_error(f"参数错误: {e}")
    
    def _prompt_select_anime(self, max_index: int) -> int | None:
        """提示用户选择动画"""
        while True:
            try:
                user_input = input(f"\n请选择要添加的动画（输入ID，如 1-{max_index}，或 q 取消）: ").strip()
                
                if user_input.lower() == 'q':
                    self._print_info("已取消操作")
                    return None
                
                index = int(user_input)
                if 1 <= index <= max_index:
                    return index
                else:
                    self._print_error(f"请输入 1-{max_index} 之间的数字")
            except ValueError:
                self._print_error("请输入有效的数字")
            except KeyboardInterrupt:
                self._print_info("\n已取消操作")
                return None
    
    def _prompt_select_rss(self, max_index: int) -> list[int] | None:
        """提示用户选择RSS源（支持多选）"""
        while True:
            try:
                user_input = input(f"\n请选择要添加的RSS源（可多选，如 1,2 或 1-3，或 q 取消）: ").strip()
                
                if user_input.lower() == 'q':
                    self._print_info("已取消RSS源添加")
                    return []
                
                # 解析用户输入
                indices = []
                parts = user_input.split(',')
                
                for part in parts:
                    part = part.strip()
                    if '-' in part:
                        # 范围选择，如 1-3
                        start, end = part.split('-')
                        start = int(start.strip())
                        end = int(end.strip())
                        indices.extend(range(start, end + 1))
                    else:
                        # 单个选择
                        indices.append(int(part))
                
                # 验证索引
                indices = list(set(indices))  # 去重
                indices.sort()
                
                if all(1 <= idx <= max_index for idx in indices):
                    return indices
                else:
                    self._print_error(f"请输入 1-{max_index} 之间的数字或范围")
            except ValueError:
                self._print_error("请输入有效的数字或范围（如 1,2 或 1-3）")
            except KeyboardInterrupt:
                self._print_info("\n已取消RSS源添加")
                return []
    
    def _anime_help(self):
        """显示 anime 命令的帮助信息"""
        help_text = """
动画相关命令

用法: anime <子命令> [选项]

子命令:
  add         添加动画
  list        列出所有动画
  show        显示动画详情
  smart-add   智能添加动画（从链接自动解析）

使用 'anime <子命令> --help' 查看子命令的详细帮助
        """
        self.console.print(help_text)
    
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