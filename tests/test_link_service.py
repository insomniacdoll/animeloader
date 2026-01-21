"""
链接服务测试
"""
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server.database import init_database, get_db
from server.services.link_service import LinkService
from server.services.anime_service import AnimeService
from server.services.rss_service import RSSService
from test_base import BaseTest


def test_link_service():
    """测试链接服务"""
    test = BaseTest("链接服务")
    
    def run_test():
        db = next(get_db())
        
        # 创建测试数据
        anime_service = AnimeService(db)
        rss_service = RSSService(db)
        link_service = LinkService(db)
        
        # 创建动画
        anime = anime_service.create_anime(
            title="测试动画",
            title_en="Test Anime",
            description="这是一个测试动画",
            status="ongoing",
            total_episodes=12
        )
        print(f"✓ 创建动画: {anime.title} (ID: {anime.id})")
        
        # 创建RSS源
        rss_source = rss_service.create_rss_source(
            anime_id=anime.id,
            name="测试RSS源",
            url="https://example.com/rss",
            quality="1080p",
            auto_download=True
        )
        print(f"✓ 创建RSS源: {rss_source.name} (ID: {rss_source.id})")
        
        # 测试1: 添加链接
        link1 = link_service.add_link(
            rss_source_id=rss_source.id,
            episode_number=1,
            episode_title="第1集",
            link_type="magnet",
            url="magnet:?xt=urn:btih:test123",
            file_size=1024 * 1024 * 1024  # 1GB
        )
        print(f"✓ 添加链接: {link1.episode_title} (ID: {link1.id})")
        
        # 测试2: 添加另一个链接
        link2 = link_service.add_link(
            rss_source_id=rss_source.id,
            episode_number=2,
            episode_title="第2集",
            link_type="magnet",
            url="magnet:?xt=urn:btih:test456",
            file_size=1024 * 1024 * 1024  # 1GB
        )
        print(f"✓ 添加链接: {link2.episode_title} (ID: {link2.id})")
        
        # 测试3: 获取链接
        link = link_service.get_link(link1.id)
        assert link is not None
        assert link.episode_title == "第1集"
        print(f"✓ 获取链接: {link.episode_title} (ID: {link.id})")
        
        # 测试4: 获取RSS源的所有链接
        links = link_service.get_links(rss_source.id)
        assert len(links) == 2
        print(f"✓ 获取RSS源的所有链接: 共 {len(links)} 个")
        
        # 测试5: 统计链接数量
        count = link_service.count_links(rss_source_id=rss_source.id)
        assert count == 2
        print(f"✓ 统计链接数量: {count} 个")
        
        # 测试6: 按类型过滤链接
        magnet_links = link_service.filter_links_by_type(rss_source.id, "magnet")
        assert len(magnet_links) == 2
        print(f"✓ 按类型过滤链接: magnet 类型共 {len(magnet_links)} 个")
        
        # 测试7: 获取可用链接
        available_links = link_service.get_available_links(rss_source.id)
        assert len(available_links) == 2
        print(f"✓ 获取可用链接: 共 {len(available_links)} 个")
        
        # 测试8: 标记链接为已下载
        link_service.mark_as_downloaded(link1.id)
        downloaded_links = link_service.get_links(rss_source.id, is_downloaded=True)
        assert len(downloaded_links) == 1
        print(f"✓ 标记链接为已下载: {link1.episode_title}")
        
        # 测试9: 更新链接状态
        link_service.update_link_status(link2.id, is_available=False)
        updated_link = link_service.get_link(link2.id)
        assert updated_link.is_available is False
        print(f"✓ 更新链接状态: {updated_link.episode_title} 不可用")
        
        # 测试10: 获取所有链接
        all_links = link_service.get_all_links()
        assert len(all_links) >= 2
        print(f"✓ 获取所有链接: 共 {len(all_links)} 个")
        
        # 测试11: 删除链接
        success = link_service.delete_link(link1.id)
        assert success is True
        print(f"✓ 删除链接: ID {link1.id}")
        
        # 验证删除
        link = link_service.get_link(link1.id)
        assert link is None
        print(f"✓ 验证删除成功")
    
    test.run_test(run_test)


if __name__ == "__main__":
    test_link_service()