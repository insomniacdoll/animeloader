"""
下载器服务测试
"""
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server.database import init_database, get_db
from server.services.downloader_service import DownloaderService
from server.utils import config, init_config
from test_utils import TestEnvironment


def test_downloader_service():
    """测试下载器服务"""
    print("=" * 60)
    print("测试下载器服务")
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
        
        downloader_service = DownloaderService(db)
        
        # 清理现有下载器
        existing_downloaders = downloader_service.get_downloaders()
        for d in existing_downloaders:
            downloader_service.delete_downloader(d.id)
        
        # 测试1: 添加下载器
        downloader1 = downloader_service.add_downloader(
            name="Mock下载器",
            downloader_type="mock",
            config={"host": "127.0.0.1", "port": 6800},
            is_default=True,
            max_concurrent_tasks=3
        )
        print(f"✓ 添加下载器: {downloader1.name} (ID: {downloader1.id})")
        
        # 测试2: 添加另一个下载器
        downloader2 = downloader_service.add_downloader(
            name="Aria2下载器",
            downloader_type="aria2",
            config={"host": "127.0.0.1", "port": 6800},
            is_default=False,
            max_concurrent_tasks=5
        )
        print(f"✓ 添加下载器: {downloader2.name} (ID: {downloader2.id})")
        
        # 测试3: 获取单个下载器
        downloader = downloader_service.get_downloader(downloader1.id)
        assert downloader is not None
        assert downloader.name == "Mock下载器"
        print(f"✓ 获取下载器: {downloader.name} (ID: {downloader.id})")
        
        # 测试4: 获取所有下载器
        downloaders = downloader_service.get_downloaders()
        assert len(downloaders) == 2
        print(f"✓ 获取所有下载器: 共 {len(downloaders)} 个")
        
        # 测试5: 获取默认下载器
        default_downloader = downloader_service.get_default_downloader()
        assert default_downloader is not None
        assert default_downloader.name == "Mock下载器"
        print(f"✓ 获取默认下载器: {default_downloader.name}")
        
        # 测试6: 按类型获取下载器
        aria2_downloader = downloader_service.get_downloader_by_type("aria2")
        assert aria2_downloader is not None
        assert aria2_downloader.name == "Aria2下载器"
        print(f"✓ 按类型获取下载器: {aria2_downloader.name}")
        
        # 测试7: 更新下载器
        updated_downloader = downloader_service.update_downloader(
            downloader_id=downloader1.id,
            name="Mock下载器(已更新)",
            config={"host": "127.0.0.1", "port": 6801}
        )
        assert updated_downloader is not None
        assert updated_downloader.name == "Mock下载器(已更新)"
        print(f"✓ 更新下载器: {updated_downloader.name}")
        
        # 测试8: 测试下载器连接
        result = downloader_service.test_downloader(downloader1.id)
        assert result["success"] is True
        print(f"✓ 测试下载器连接: 下载器 '{updated_downloader.name}' 连接测试成功")
        
        # 测试9: 获取下载器状态
        status = downloader_service.get_downloader_status(downloader1.id)
        assert status is not None
        print(f"✓ 获取下载器状态: {updated_downloader.name}")
        
        # 测试10: 设置默认下载器
        downloader_service.set_default_downloader(downloader2.id)
        default_downloader = downloader_service.get_default_downloader()
        assert default_downloader.id == downloader2.id
        print(f"✓ 设置默认下载器: {default_downloader.name}")
        
        # 测试11: 验证旧默认下载器已取消
        old_default = downloader_service.get_downloader(downloader1.id)
        assert old_default.is_default is False
        print(f"✓ 验证旧默认下载器已取消: {old_default.name}")
        
        # 测试12: 获取支持的下载器类型
        types = downloader_service.get_supported_downloader_types()
        assert len(types) > 0
        print(f"✓ 获取支持的下载器类型: {', '.join(types)}")
        
        # 测试13: 验证下载器配置
        valid, message = downloader_service.validate_downloader_config("mock", {})
        assert valid is True
        print(f"✓ 验证下载器配置: {message}")
        
        # 测试14: 删除下载器
        success = downloader_service.delete_downloader(downloader1.id)
        assert success is True
        print(f"✓ 删除下载器: ID {downloader1.id}")
        
        # 验证删除
        downloader = downloader_service.get_downloader(downloader1.id)
        assert downloader is None
        print(f"✓ 验证删除成功")
        
        print("\n" + "=" * 60)
        print("[成功] 下载器服务测试通过")
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
    test_downloader_service()