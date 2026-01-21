"""
测试智能添加功能
使用测试隔离环境
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from client.api.client import APIClient
from rich.console import Console
from rich.table import Table
from tests.test_utils import TestEnvironment


def get_default_api_key(env: TestEnvironment):
    """获取默认API密钥"""
    try:
        from server.utils import init_config
        from server.database import get_db, get_engine
        from server.services.api_key_service import APIKeyService
        from server.models import Base
        
        # 初始化配置（使用测试环境的配置文件）
        init_config(env.get_config_path())
        
        # 初始化数据库
        engine = get_engine()
        Base.metadata.create_all(bind=engine)
        
        # 获取数据库会话
        SessionLocal = next(get_db())
        try:
            api_key_service = APIKeyService(SessionLocal)
            default_key = api_key_service.get_default_api_key()
            return default_key.key if default_key else None
        finally:
            SessionLocal.close()
    except Exception as e:
        print(f"获取API密钥失败: {e}")
        return None


def test_smart_add_interaction(env: TestEnvironment):
    """测试智能添加的交互流程"""
    try:
        print("=" * 60)
        print("测试智能添加交互流程")
        print("=" * 60)
        
        # 打印测试环境信息
        env.print_info()
        
        # 启动服务端
        if not env.start_server():
            print("✗ 服务端启动失败")
            return False
        
        console = Console()
        
        # 获取 API key
        api_key = get_default_api_key(env)
        
        # 初始化API客户端
        api_client = APIClient(base_url=env.get_server_url(), api_key=api_key)
        
        test_url = "https://mikanani.me/Home/Bangumi/3824"
        
        # 步骤1: 智能解析
        console.print(f"\n步骤1: 智能解析")
        console.print(f"URL: {test_url}")
        
        parse_response = api_client.post('/api/anime/smart-parse', json_data={'url': test_url})
        
        if 'error' in parse_response:
            console.print(f"解析失败: {parse_response['error']}")
            return False
        
        site_name = parse_response.get('site_name', 'Unknown')
        anime_list = parse_response.get('results', [])
        
        if not anime_list:
            console.print("未能解析到动画信息")
            return False
        
        console.print(f"✓ 成功从 {site_name} 解析到 {len(anime_list)} 个动画")
        
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
        
        console.print(table)
        
        # 选择动画
        if len(anime_list) == 1:
            selected_index = 1
        else:
            selected_index = 1
        
        selected_anime = anime_list[selected_index - 1]
        
        # 检查是否有RSS源
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
                    rss.get('name', ''),
                    rss.get('url', ''),
                    rss.get('quality', ''),
                    "是" if rss.get('auto_download') else "否"
                )
            
            console.print(rss_table)
            
            console.print("\n[yellow]注意: 客户端应该让用户选择要添加的RSS源[/yellow]")
            console.print("[yellow]（当前测试模拟选择所有RSS源）[/yellow]")
            
            # 模拟添加所有RSS源
            rss_indices = list(range(1, len(rss_sources) + 1))
        else:
            console.print("[yellow]没有找到RSS源[/yellow]")
        
        # 步骤2: 智能添加
        console.print(f"\n步骤2: 智能添加动画")
        
        add_response = api_client.post('/api/anime/smart-add', json_data={
            'url': test_url,
            'auto_add_rss': True,
            'anime_index': selected_index,
            'rss_indices': rss_indices
        })
        
        if 'error' in add_response:
            console.print(f"[red]添加失败: {add_response['error']}[/red]")
            return False
        
        anime = add_response.get('anime')
        if anime:
            console.print(f"\n[green]✓[/green] 动画添加成功: [cyan]{anime['title']}[/cyan]")
            console.print(f"ID: {anime['id']}")
        
        added_rss_sources = add_response.get('rss_sources', [])
        if added_rss_sources:
            console.print(f"\n[green]✓[/green] 成功添加 {len(added_rss_sources)} 个RSS源:")
            for rss in added_rss_sources:
                console.print(f"  - [cyan]{rss['name']}[/cyan] (ID: {rss['id']})")
        
        console.print("\n" + "=" * 60)
        console.print("[green]测试完成[/green]")
        console.print("=" * 60)
        
        return True
    
    except Exception as e:
        console.print(f"\n[red]测试失败: {e}[/red]")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    env = TestEnvironment()
    try:
        env.setup()
        success = test_smart_add_interaction(env)
        return 0 if success else 1
    except Exception as e:
        print(f"\n[失败] 发生错误: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        env.teardown()


if __name__ == "__main__":
    sys.exit(main())