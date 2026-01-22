"""
测试API端点重复添加行为
使用测试隔离环境
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from client.api.client import APIClient
from tests.test_utils import TestEnvironment
import requests


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


def test_api_duplicate_prevention(env: TestEnvironment):
    """测试API重复添加预防功能"""
    print("=" * 60)
    print("测试API重复添加预防功能")
    print("=" * 60)
    
    # 启动服务端
    print("启动服务端...")
    if not env.start_server():
        print("✗ 服务端启动失败")
        return False
    
    # 获取API密钥
    api_key = get_default_api_key(env)
    if not api_key:
        print("✗ 无法获取API密钥")
        return False
    
    print(f"✓ API密钥获取成功: {api_key[:8]}...")
    
    # 初始化API客户端
    api_client = APIClient(base_url=env.get_server_url(), api_key=api_key)
    
    try:
        print("\n1. 测试动画重复添加...")
        # 添加第一个动画
        anime_data1 = {
            "title": "API测试动画",
            "title_en": "API Test Anime",
            "description": "测试动画描述",
            "cover_url": "https://example.com/cover.jpg",
            "source_url": "https://example.com/anime/test"
        }
        
        response1 = api_client.post('/api/anime', json_data=anime_data1)
        
        if 'error' not in response1 and 'id' in response1:
            anime1 = response1
            print(f"   ✓ 成功创建动画: {anime1['title']} (ID: {anime1['id']})")
        else:
            print(f"   ✗ 创建动画失败: {response1}")
            return False
        
        # 尝试添加相同source_url的动画
        anime_data2 = {
            "title": "API测试动画重复",
            "title_en": "API Test Anime Duplicate",
            "description": "重复动画描述",
            "cover_url": "https://example.com/cover2.jpg",
            "source_url": "https://example.com/anime/test"  # 相同的source_url
        }
        
        response2 = api_client.post('/api/anime', json_data=anime_data2)
        
        if 'error' not in response2 and 'id' in response2:
            anime2 = response2
            print(f"   ✓ 尝试创建重复动画: {anime2['title']} (ID: {anime2['id']})")
            
            if anime1['id'] == anime2['id']:
                print("   ✓ 动画重复添加被正确阻止，返回了相同的ID")
            else:
                print("   ✗ 动画重复添加未被阻止，返回了不同的ID")
                return False
        else:
            print(f"   ✗ 尝试创建重复动画失败: {response2}")
            return False
        
        print(f"\n2. 测试RSS源重复添加...")
        # 添加第一个RSS源
        rss_data1 = {
            "anime_id": anime1['id'],
            "name": "API测试RSS源",
            "url": "https://example.com/rss/test",
            "quality": "1080p"
        }
        
        response3 = api_client.post('/api/rss-sources', json_data=rss_data1)
        
        if 'error' not in response3 and 'id' in response3:
            rss1 = response3
            print(f"   ✓ 成功创建RSS源: {rss1['name']} (ID: {rss1['id']})")
        else:
            print(f"   ✗ 创建RSS源失败: {response3}")
            return False
        
        # 尝试添加相同URL的RSS源到同一个动画
        rss_data2 = {
            "anime_id": anime1['id'],  # 同一个动画
            "name": "API测试RSS源重复",
            "url": "https://example.com/rss/test",  # 相同的URL
            "quality": "720p"
        }
        
        response4 = api_client.post('/api/rss-sources', json_data=rss_data2)
        
        if 'error' not in response4 and 'id' in response4:
            rss2 = response4
            print(f"   ✓ 尝试创建重复RSS源: {rss2['name']} (ID: {rss2['id']})")
            
            if rss1['id'] == rss2['id']:
                print("   ✓ RSS源重复添加被正确阻止，返回了相同的ID")
            else:
                print("   ✗ RSS源重复添加未被阻止，返回了不同的ID")
                return False
        else:
            print(f"   ✗ 尝试创建重复RSS源失败: {response4}")
            return False
        
        print(f"\n3. 测试链接重复添加...")
        # 添加第一个链接
        link_data1 = {
            "rss_source_id": rss1['id'],
            "episode_number": 1,
            "episode_title": "第1集",
            "link_type": "magnet",
            "url": "magnet:?xt=hash123"
        }
        
        response5 = api_client.post('/api/links', json_data=link_data1)
        
        if 'error' not in response5 and 'id' in response5:
            link1 = response5
            print(f"   ✓ 成功创建链接: {link1['url']} (ID: {link1['id']})")
        else:
            print(f"   ✗ 创建链接失败: {response5}")
            return False
        
        # 尝试添加相同URL的链接到同一个RSS源
        link_data2 = {
            "rss_source_id": rss1['id'],  # 同一个RSS源
            "episode_number": 2,  # 不同的集数
            "episode_title": "第2集",
            "link_type": "magnet",
            "url": "magnet:?xt=hash123"  # 相同的URL
        }
        
        response6 = api_client.post('/api/links', json_data=link_data2)
        
        if 'error' not in response6 and 'id' in response6:
            link2 = response6
            print(f"   ✓ 尝试创建重复链接: {link2['url']} (ID: {link2['id']})")
            
            if link1['id'] == link2['id']:
                print("   ✓ 链接重复添加被正确阻止，返回了相同的ID")
            else:
                print("   ✗ 链接重复添加未被阻止，返回了不同的ID")
                return False
        else:
            print(f"   ✗ 尝试创建重复链接失败: {response6}")
            return False
        
        print("\n" + "=" * 60)
        print("[成功] 所有API重复添加预防测试通过")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"[错误] 测试过程中出现异常: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    env = TestEnvironment()
    try:
        env.setup()
        success = test_api_duplicate_prevention(env)
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