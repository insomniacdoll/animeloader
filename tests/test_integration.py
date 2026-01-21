"""
集成测试 - 测试完整的RSS检查和链接提取流程
"""
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server.database import init_database, get_db
from server.services.anime_service import AnimeService
from server.services.rss_service import RSSService
from server.services.link_service import LinkService
from server.services.scheduler_service import SchedulerService
from server.utils import config, init_config
from test_utils import TestEnvironment


def test_integration():
    """测试完整的RSS检查和链接提取流程"""
    print("=" * 60)
    print("集成测试 - RSS检查和链接提取流程")
    print("=" * 60)
    
    # 设置测试环境
    env = TestEnvironment()
    temp_dir = None
    
    try:
        temp_dir = env.setup()
        
        # 打印测试环境信息
        env.print_info()
        
        # 初始化配置
        cfg = init_config(env.get_config_path())
        
        # 打印配置信息
        cfg.print_info()
        
        # 初始化数据库
        init_database()
        
        # 创建服务
        db = next(get_db())
        anime_service = AnimeService(db)
        rss_service = RSSService(db)
        link_service = LinkService(db)
        scheduler_service = SchedulerService(get_db)
        
        # 步骤1: 创建测试动画
        print("\n步骤1: 创建测试动画")
        anime = anime_service.create_anime(
            title="黄金神威 最终章",
            title_en="Golden Kamuy Final Season",
            description="黄金神威最终季",
            status="ongoing",
            total_episodes=12
        )
        print(f"✓ 创建动画: {anime.title} (ID: {anime.id})")
        
        # 步骤2: 创建RSS源
        print("\n步骤2: 创建RSS源")
        rss_source = rss_service.create_rss_source(
            anime_id=anime.id,
            name="蜜柑计划 RSS",
            url="https://mikanani.me/RSS/Bangumi?bangumiId=3824",
            quality="1080p",
            auto_download=False
        )
        print(f"✓ 创建RSS源: {rss_source.name} (ID: {rss_source.id})")
        print(f"  URL: {rss_source.url}")
        
        # 步骤3: 检查RSS源并提取链接
        print("\n步骤3: 检查RSS源并提取链接")
        result = scheduler_service.check_rss_source(rss_source.id, auto_download=False)
        
        assert result['success'] is True, f"检查RSS源失败: {result.get('message')}"
        print(f"✓ 检查完成: {result['message']}")
        print(f"  发现新链接数: {result.get('new_links_count', 0)}")
        
        # 步骤4: 验证链接已添加到数据库
        print("\n步骤4: 验证链接已添加到数据库")
        links = link_service.get_links(rss_source.id)
        print(f"✓ 数据库中的链接数: {len(links)}")
        
        if len(links) > 0:
            print(f"\n前5个链接:")
            for i, link in enumerate(links[:5], 1):
                print(f"  {i}. 第{link.episode_number}集 - {link.episode_title}")
                print(f"     类型: {link.link_type}, 大小: {link.file_size / (1024**3):.2f} GB")
                print(f"     URL: {link.url[:50]}...")
        
        # 步骤5: 再次检查RSS源（应该没有新链接）
        print("\n步骤5: 再次检查RSS源（应该没有新链接）")
        result = scheduler_service.check_rss_source(rss_source.id, auto_download=False)
        print(f"✓ 检查完成: {result['message']}")
        
        # 步骤6: 测试按集数过滤
        print("\n步骤6: 测试按集数过滤")
        if len(links) > 0:
            episode_number = links[0].episode_number
            episode_links = link_service.get_links(rss_source.id)
            episode_links = [l for l in episode_links if l.episode_number == episode_number]
            print(f"✓ 第{episode_number}集的链接数: {len(episode_links)}")
            if len(episode_links) > 0:
                for link in episode_links:
                    print(f"  - {link.episode_title} ({link.link_type})")
        
        # 步骤7: 测试统计链接
        print("\n步骤7: 测试统计链接")
        total_count = link_service.count_links(rss_source_id=rss_source.id)
        print(f"✓ 总链接数: {total_count}")
        
        # 按类型统计
        for link_type in ["magnet", "ed2k", "torrent"]:
            count = link_service.count_links(rss_source_id=rss_source.id, link_type=link_type)
            if count > 0:
                print(f"  - {link_type}: {count}")
        
        # 步骤8: 测试获取可用链接
        print("\n步骤8: 测试获取可用链接")
        available_links = link_service.get_available_links(rss_source.id)
        print(f"✓ 可用链接数: {len(available_links)}")
        
        # 步骤9: 测试标记为已下载
        print("\n步骤9: 测试标记为已下载")
        if len(links) > 0:
            test_link = links[0]
            link_service.mark_as_downloaded(test_link.id)
            print(f"✓ 标记链接 {test_link.id} 为已下载")
            
            # 验证
            updated_link = link_service.get_link(test_link.id)
            assert updated_link.is_downloaded is True
            print("✓ 验证成功")
        
        # 步骤10: 测试更新链接状态
        print("\n步骤10: 测试更新链接状态")
        if len(links) > 1:
            test_link = links[1]
            link_service.update_link_status(test_link.id, is_available=False)
            print(f"✓ 更新链接 {test_link.id} 为不可用")
            
            # 验证
            updated_link = link_service.get_link(test_link.id)
            assert updated_link.is_available is False
            print("✓ 验证成功")
        
        print("\n" + "=" * 60)
        print("[成功] 集成测试通过")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n[失败] 测试失败: {e}")
        db.rollback()
        raise
    except Exception as e:
        print(f"\n[失败] 发生错误: {e}")
        db.rollback()
        raise
    finally:
        # 清理测试环境
        env.teardown()
        print(f"已清理测试环境: {temp_dir}")


if __name__ == "__main__":
    test_integration()