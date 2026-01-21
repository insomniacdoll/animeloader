"""
调度服务测试
"""
import sys
import os
import time

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server.database import init_database, get_db
from server.services.scheduler_service import SchedulerService
from server.services.anime_service import AnimeService
from server.services.rss_service import RSSService
from server.utils import config, init_config
from test_utils import TestEnvironment


def test_scheduler_service():
    """测试调度服务"""
    print("=" * 60)
    print("测试调度服务")
    print("=" * 60)
    
    # 设置测试环境
    env = TestEnvironment()
    temp_dir = None
    scheduler_service = None
    
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
    
        # 创建调度器服务
        scheduler_service = SchedulerService(get_db)
        
        # 测试1: 启动调度器
        success = scheduler_service.start_scheduler()
        assert success is True
        assert scheduler_service.is_running is True
        print(f"✓ 启动调度器")
        
        # 创建测试数据
        db = next(get_db())
        anime_service = AnimeService(db)
        rss_service = RSSService(db)
        
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
            name="蜜柑计划 RSS",
            url="https://mikanani.me/RSS/Bangumi?bangumiId=3824",
            quality="1080p",
            auto_download=True
        )
        print(f"✓ 创建RSS源: {rss_source.name} (ID: {rss_source.id})")
        db.close()
        
        # 测试2: 添加检查任务
        job_id = scheduler_service.add_check_job(
            rss_source_id=rss_source.id,
            interval=10,  # 10秒
            auto_download=False
        )
        assert job_id is not None
        print(f"✓ 添加检查任务: {job_id}")
        
        # 测试3: 获取所有任务
        jobs = scheduler_service.get_jobs()
        assert len(jobs) >= 1
        print(f"✓ 获取所有任务: 共 {len(jobs)} 个")
        
        # 测试4: 获取任务状态
        job_status = scheduler_service.get_job_status(job_id)
        assert job_status is not None
        assert job_status["job_id"] == job_id
        print(f"✓ 获取任务状态: {job_status['name']}")
        
        # 测试5: 手动检查RSS源
        result = scheduler_service.check_rss_source(rss_source.id, auto_download=False)
        assert result["success"] is True
        print(f"✓ 手动检查RSS源: {result['message']}")
        
        # 测试6: 暂停任务
        success = scheduler_service.pause_job(job_id)
        assert success is True
        print(f"✓ 暂停任务: {job_id}")
        
        # 测试7: 恢复任务
        success = scheduler_service.resume_job(job_id)
        assert success is True
        print(f"✓ 恢复任务: {job_id}")
        
        # 测试8: 移除任务
        success = scheduler_service.remove_check_job(job_id)
        assert success is True
        print(f"✓ 移除任务: {job_id}")
        
        # 验证移除
        job_status = scheduler_service.get_job_status(job_id)
        assert job_status is None
        print(f"✓ 验证任务已移除")
        
        # 测试9: 获取支持的RSS源网站
        supported_sites = scheduler_service.get_supported_rss_sites()
        assert len(supported_sites) > 0
        print(f"✓ 获取支持的RSS源网站: {', '.join(supported_sites)}")
        
        # 测试10: 测试解析器选择
        parser = scheduler_service._get_rss_parser("https://mikanani.me/RSS/Bangumi?bangumiId=3824")
        assert parser is not None
        print(f"✓ 解析器选择: {parser.get_site_name()}")
        
        # 测试11: 测试不支持的RSS源
        parser = scheduler_service._get_rss_parser("https://example.com/rss")
        assert parser is None
        print(f"✓ 不支持的RSS源: 返回None")
        
        # 测试12: 添加另一个任务并测试自动下载
        job_id2 = scheduler_service.add_check_job(
            rss_source_id=rss_source.id,
            interval=10,
            auto_download=True
        )
        assert job_id2 is not None
        print(f"✓ 添加自动下载任务: {job_id2}")
        
        # 测试13: 手动检查RSS源（带自动下载）
        result = scheduler_service.check_rss_source(rss_source.id, auto_download=True)
        assert result["success"] is True
        print(f"✓ 手动检查RSS源（自动下载）: {result['message']}")
        
        # 等待一小段时间让调度器运行
        time.sleep(2)
        
        # 测试14: 停止调度器
        success = scheduler_service.stop_scheduler()
        assert success is True
        assert scheduler_service.is_running is False
        print(f"✓ 停止调度器")
        
        # 验证任务已清除
        jobs = scheduler_service.get_jobs()
        assert len(jobs) == 0
        print(f"✓ 验证任务已清除")
        
        print("\n" + "=" * 60)
        print("[成功] 调度服务测试通过")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n[失败] 测试失败: {e}")
        if scheduler_service is not None and scheduler_service.is_running:
            scheduler_service.stop_scheduler()
        raise
    except Exception as e:
        print(f"\n[失败] 发生错误: {e}")
        if scheduler_service is not None and scheduler_service.is_running:
            scheduler_service.stop_scheduler()
        raise
    finally:
        # 清理测试环境
        env.teardown()
        print(f"已清理测试环境: {temp_dir}")


if __name__ == "__main__":
    test_scheduler_service()