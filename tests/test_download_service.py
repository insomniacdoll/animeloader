"""
下载服务测试
"""
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server.database import init_database, get_db
from server.services.download_service import DownloadService
from server.services.link_service import LinkService
from server.services.downloader_service import DownloaderService
from server.services.anime_service import AnimeService
from server.services.rss_service import RSSService
from server.utils import config, init_config
from test_utils import TestEnvironment


def test_download_service():
    """测试下载服务"""
    print("=" * 60)
    print("测试下载服务")
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
        db = next(get_db())
        
        # 创建服务实例
        anime_service = AnimeService(db)
        rss_service = RSSService(db)
        link_service = LinkService(db)
        downloader_service = DownloaderService(db)
        download_service = DownloadService(db)
        
        # 创建测试数据
        anime = anime_service.create_anime(
            title="测试动画",
            title_en="Test Anime",
            description="这是一个测试动画",
            status="ongoing",
            total_episodes=12
        )
        print(f"✓ 创建动画: {anime.title} (ID: {anime.id})")
        
        rss_source = rss_service.create_rss_source(
            anime_id=anime.id,
            name="测试RSS源",
            url="https://example.com/rss",
            quality="1080p",
            auto_download=True
        )
        print(f"✓ 创建RSS源: {rss_source.name} (ID: {rss_source.id})")
        
        link = link_service.add_link(
            rss_source_id=rss_source.id,
            episode_number=1,
            episode_title="第1集",
            link_type="magnet",
            url="magnet:?xt=urn:btih:test123",
            file_size=1024 * 1024 * 1024  # 1GB
        )
        print(f"✓ 创建链接: {link.episode_title} (ID: {link.id})")
        
        downloader = downloader_service.add_downloader(
            name="Mock下载器",
            downloader_type="mock",
            config={"host": "localhost", "port": 6800}
        )
        print(f"✓ 创建下载器: {downloader.name} (ID: {downloader.id})")
        
        # 测试1: 创建下载任务
        task = download_service.create_download_task(
            link_id=link.id,
            rss_source_id=rss_source.id,
            downloader_id=downloader.id
        )
        print(f"✓ 创建下载任务: ID {task.id}, 状态 {task.status}")
        
        # 测试2: 获取下载任务
        task = download_service.get_download_task(task.id)
        assert task is not None
        print(f"✓ 获取下载任务: ID {task.id}")
        
        # 测试3: 获取RSS源的下载任务
        tasks = download_service.get_download_tasks(rss_source_id=rss_source.id)
        assert len(tasks) >= 1
        print(f"✓ 获取RSS源的下载任务: 共 {len(tasks)} 个")
        
        # 测试4: 获取所有下载任务
        tasks = download_service.get_download_tasks()
        assert len(tasks) >= 1
        print(f"✓ 获取所有下载任务: 共 {len(tasks)} 个")
        
        # 测试5: 统计下载任务数量
        count = download_service.count_download_tasks()
        assert count >= 1
        print(f"✓ 统计下载任务数量: {count} 个")
        
        # 测试6: 开始下载
        download_service.start_download(task.id)
        task = download_service.get_download_task(task.id)
        assert task.status == "downloading"
        print(f"✓ 开始下载: ID {task.id}, 状态 {task.status}")
        
        # 测试7: 获取下载状态
        status_info = download_service.get_download_status(task.id)
        assert status_info is not None
        assert status_info["status"] == "downloading"
        print(f"✓ 获取下载状态: {status_info['status']}")
        
        # 测试8: 暂停下载
        download_service.pause_download(task.id)
        task = download_service.get_download_task(task.id)
        assert task.status == "paused"
        print(f"✓ 暂停下载: ID {task.id}, 状态 {task.status}")
        
        # 测试9: 恢复下载
        download_service.resume_download(task.id)
        task = download_service.get_download_task(task.id)
        assert task.status == "downloading"
        print(f"✓ 恢复下载: ID {task.id}, 状态 {task.status}")
        
        # 测试10: 同步下载状态
        download_service.sync_download_status(task.id)
        task = download_service.get_download_task(task.id)
        # Mock 实现会自动增加进度
        assert task.progress >= 0
        print(f"✓ 同步下载状态: 进度 {task.progress}%")
        
        # 测试11: 取消下载
        download_service.cancel_download(task.id)
        task = download_service.get_download_task(task.id)
        assert task.status == "cancelled"
        print(f"✓ 取消下载: ID {task.id}, 状态 {task.status}")
        
        # 测试12: 模拟下载完成
        task2 = download_service.create_download_task(
            link_id=link.id,
            rss_source_id=rss_source.id,
            downloader_id=downloader.id
        )
        download_service.start_download(task2.id)
        # 多次同步状态直到完成
        for _ in range(10):
            download_service.sync_download_status(task2.id)
            task2 = download_service.get_download_task(task2.id)
            if task2.status == "completed":
                break
        assert task2.status == "completed"
        print(f"✓ 模拟下载完成: ID {task2.id}, 状态 {task2.status}")
        
        # 测试13: 获取活跃的下载任务
        active_tasks = download_service.get_active_downloads()
        assert len(active_tasks) == 0
        print(f"✓ 获取活跃的下载任务: 共 {len(active_tasks)} 个")
        
        # 测试14: 删除下载任务
        success = download_service.delete_download_task(task.id)
        assert success is True
        print(f"✓ 删除下载任务: ID {task.id}")
        
        # 验证删除
        task = download_service.get_download_task(task.id)
        assert task is None
        print(f"✓ 验证删除成功")
        
        print("\n" + "=" * 60)
        print("[成功] 下载服务测试通过")
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
    test_download_service()