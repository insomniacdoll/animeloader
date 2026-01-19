from cmd2 import CommandSet, with_argparser, with_default_category
import argparse
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm


@with_default_category('anime')
class AnimeCommands(CommandSet):
    """动画相关命令"""
    
    def __init__(self, api_client=None):
        super().__init__()
        self.console = Console()
        self.api_client = api_client
    
    add_parser = argparse.ArgumentParser()
    add_parser.add_argument('--title', required=True, help='动画标题')
    add_parser.add_argument('--title-en', help='英文标题')
    add_parser.add_argument('--description', help='描述')
    add_parser.add_argument('--cover-url', help='封面URL')
    add_parser.add_argument('--status', default='ongoing', help='状态 (ongoing, completed)')
    add_parser.add_argument('--total-episodes', type=int, help='总集数')
    
    @with_argparser(add_parser)
    def do_add(self, args):
        """添加动画"""
        # TODO: 实现添加动画的逻辑
        self.console.print(f"添加动画: {args.title}")
        if args.title_en:
            self.console.print(f"英文标题: {args.title_en}")
        if args.description:
            self.console.print(f"描述: {args.description}")
        self.console.print("[yellow]功能实现中...[/yellow]")
    
    smart_add_parser = argparse.ArgumentParser()
    smart_add_parser.add_argument('--url', required=True, help='动画网站链接')
    smart_add_parser.add_argument('--auto-add-rss', action='store_true', default=True, help='是否自动解析RSS源')
    smart_add_parser.add_argument('--no-rss', action='store_true', help='不解析RSS源')
    
    @with_argparser(smart_add_parser)
    def do_smart_add(self, args):
        """智能添加动画（从链接自动解析）"""
        if self.api_client is None:
            self.console.print("[red]API客户端未初始化[/red]")
            return
        
        self.console.print(f"正在解析链接: {args.url}")
        
        # 调用服务端API进行智能解析
        response = self.api_client.post('/api/anime/smart-parse', json_data={'url': args.url})
        
        if 'error' in response:
            self.console.print(f"[red]解析失败: {response['error']}[/red]")
            return
        
        site_name = response.get('site_name', 'Unknown')
        anime_list = response.get('results', [])
        
        if not anime_list:
            self.console.print("[red]未能解析到动画信息[/red]")
            return
        
        self.console.print(f"[green]✓[/green] 成功从 [cyan]{site_name}[/cyan] 解析到 {len(anime_list)} 个动画")
        
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
                anime.get('title', ''),
                anime.get('title_en', ''),
                anime.get('status', ''),
                str(anime.get('total_episodes', 0))
            )
        
        self.console.print(table)
        
        # 选择动画
        if len(anime_list) == 1:
            selected_index = 1
        else:
            selected_index = Prompt.ask(
                "请选择要添加的动画",
                choices=[str(i) for i in range(1, len(anime_list) + 1)],
                default="1"
            )
            selected_index = int(selected_index)
        
        selected_anime = anime_list[selected_index - 1]
        
        # 确认添加
        self.console.print(f"\n即将添加动画: [cyan]{selected_anime['title']}[/cyan]")
        if selected_anime.get('title_en'):
            self.console.print(f"英文标题: {selected_anime['title_en']}")
        if selected_anime.get('description'):
            self.console.print(f"描述: {selected_anime['description']}")
        
        if not Confirm.ask("确认添加？", default=True):
            self.console.print("[yellow]已取消[/yellow]")
            return
        
        # 确定是否添加RSS源
        auto_add_rss = args.auto_add_rss and not args.no_rss
        rss_indices = []
        
        # 检查是否有RSS源
        if auto_add_rss and 'rss_sources' in selected_anime and selected_anime['rss_sources']:
            rss_sources = selected_anime['rss_sources']
            self.console.print(f"\n找到 {len(rss_sources)} 个RSS源:")
            
            rss_table = Table()
            rss_table.add_column("ID", style="cyan", width=4)
            rss_table.add_column("名称", style="magenta")
            rss_table.add_column("画质", style="green")
            rss_table.add_column("自动下载", style="yellow")
            
            for idx, rss in enumerate(rss_sources, 1):
                rss_table.add_row(
                    str(idx),
                    rss.get('name', ''),
                    rss.get('quality', ''),
                    "是" if rss.get('auto_download') else "否"
                )
            
            self.console.print(rss_table)
            
            if not Confirm.ask("是否添加RSS源？", default=True):
                auto_add_rss = False
            else:
                # 如果只有一个RSS源，自动选择
                if len(rss_sources) == 1:
                    rss_indices = [1]
                else:
                    # 多个RSS源时，让用户选择
                    rss_choice = Prompt.ask(
                        "请选择要添加的RSS源（可多选，如 1,2 或 1-3）",
                        default="1"
                    )
                    # 解析选择
                    rss_indices = []
                    if ',' in rss_choice:
                        for part in rss_choice.split(','):
                            rss_indices.append(int(part.strip()))
                    elif '-' in rss_choice:
                        start, end = map(int, rss_choice.split('-'))
                        rss_indices = list(range(start, end + 1))
                    else:
                        rss_indices = [int(rss_choice)]
        
        # 调用API添加动画
        add_response = self.api_client.post('/api/anime/smart-add', json_data={
            'url': args.url,
            'auto_add_rss': auto_add_rss,
            'anime_index': selected_index,
            'rss_indices': rss_indices
        })
        
        if 'error' in add_response:
            self.console.print(f"[red]添加失败: {add_response['error']}[/red]")
            return
        
        anime = add_response.get('anime')
        if anime:
            self.console.print(f"\n[green]✓[/green] 动画添加成功: [cyan]{anime['title']}[/cyan]")
            self.console.print(f"ID: {anime['id']}")
        
        rss_sources = add_response.get('rss_sources', [])
        if rss_sources:
            self.console.print(f"\n[green]✓[/green] 成功添加 {len(rss_sources)} 个RSS源:")
            for rss in rss_sources:
                self.console.print(f"  - [cyan]{rss['name']}[/cyan] (ID: {rss['id']})")
    
    list_parser = argparse.ArgumentParser()
    list_parser.add_argument('--keyword', help='搜索关键词')
    
    @with_argparser(list_parser)
    def do_list(self, args):
        """列出所有动画"""
        if self.api_client is None:
            self.console.print("[red]API客户端未初始化[/red]")
            return
        
        params = {}
        if args.keyword:
            params['search'] = args.keyword
        
        response = self.api_client.get('/api/anime', params=params)
        
        if 'error' in response:
            self.console.print(f"[red]获取失败: {response['error']}[/red]")
            return
        
        items = response.get('items', [])
        total = response.get('total', 0)
        
        if not items:
            self.console.print("[yellow]没有找到动画[/yellow]")
            return
        
        table = Table(title=f"动画列表 (共 {total} 个)")
        table.add_column("ID", style="cyan", width=6)
        table.add_column("标题", style="magenta")
        table.add_column("英文标题", style="green")
        table.add_column("状态", style="yellow", width=10)
        table.add_column("集数", style="blue", width=6)
        
        for anime in items:
            table.add_row(
                str(anime['id']),
                anime.get('title', ''),
                anime.get('title_en', ''),
                anime.get('status', ''),
                str(anime.get('total_episodes', 0))
            )
        
        self.console.print(table)
    
    show_parser = argparse.ArgumentParser()
    show_parser.add_argument('--id', type=int, required=True, help='动画ID')
    
    @with_argparser(show_parser)
    def do_show(self, args):
        """显示动画详情"""
        if self.api_client is None:
            self.console.print("[red]API客户端未初始化[/red]")
            return
        
        response = self.api_client.get(f'/api/anime/{args.id}')
        
        if 'error' in response:
            self.console.print(f"[red]获取失败: {response['error']}[/red]")
            return
        
        anime = response
        self.console.print(f"[cyan]标题:[/cyan] {anime.get('title', '')}")
        if anime.get('title_en'):
            self.console.print(f"[cyan]英文标题:[/cyan] {anime['title_en']}")
        if anime.get('description'):
            self.console.print(f"[cyan]描述:[/cyan] {anime['description']}")
        if anime.get('cover_url'):
            self.console.print(f"[cyan]封面:[/cyan] {anime['cover_url']}")
        self.console.print(f"[cyan]状态:[/cyan] {anime.get('status', '')}")
        if anime.get('total_episodes'):
            self.console.print(f"[cyan]总集数:[/cyan] {anime['total_episodes']}")
        self.console.print(f"[cyan]创建时间:[/cyan] {anime.get('created_at', '')}")
        self.console.print(f"[cyan]更新时间:[/cyan] {anime.get('updated_at', '')}")