
"""
测试重复添加预防功能
"""
import sys
import os
import tempfile
import shutil
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from server.database.session import get_db
from server.models import Base
from server.services.anime_service import AnimeService
from server.services.rss_service import RSSService
from server.services.link_service import LinkService


def test_duplicate_prevention():
    """测试重复添加预防功能"""
    print("=" * 60)
    print("测试重复添加预防功能")
    print("=" * 60)
    
    # 创建临时数据库文件
    temp_db_path = tempfile.mktemp(suffix='.db')
    database_url = f"sqlite:///{temp_db_path}"
    
    # 创建数据库引擎
    engine = create_engine(database_url)
    
    # 创建所有表
    Base.metadata.create_all(engine)
    
    # 创建会话
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # 创建服务实例
        anime_service = AnimeService(db)
        rss_service = RSSService(db)
        link_service = LinkService(db)
        
        print("\n1. 测试动画重复添加...")
        # 添加第一个动画
        anime1 = anime_service.create_anime(
            title="测试动画1",
            source_url="https://example.com/anime1"
        )
        print(f"   创建动画: {anime1.title} (ID: {anime1.id})")
        
        # 尝试添加相同source_url的动画
        anime2 = anime_service.create_anime(
            title="测试动画1 - 重复",
            source_url="https://example.com/anime1"
        )
        print(f"   再次添加相同URL动画: {anime2.title} (ID: {anime2.id})")
        
        if anime1.id == anime2.id:
            print("   ✓ 动画重复添加被正确阻止")
        else:
            print("   ✗ 动画重复添加未被阻止")
            return False
        
        print("\n2. 测试RSS源重复添加...")
        # 添加RSS源
        rss1 = rss_service.create_rss_source(
            anime_id=anime1.id,
            name="RSS源1",
            url="https://example.com/rss1"
        )
        print(f"   创建RSS源: {rss1.name} (ID: {rss1.id})")
        
        # 尝试添加相同URL的RSS源到同一动画
        rss2 = rss_service.create_rss_source(
            anime_id=anime1.id,
            name="RSS源1 - 重复",
            url="https://example.com/rss1"
        )
        print(f"   再次添加相同URL RSS源: {rss2.name} (ID: {rss2.id})")
        
        if rss1.id == rss2.id:
            print("   ✓ RSS源重复添加被正确阻止")
        else:
            print("   ✗ RSS源重复添加未被阻止")
            return False
        
        print("\n3. 测试链接重复添加...")
        # 添加链接
        link1 = link_service.add_link(
            rss_source_id=rss1.id,
            url="magnet:?xt=hash1",
            link_type="magnet"
        )
        print(f"   创建链接: {link1.url} (ID: {link1.id})")
        
        # 尝试添加相同URL的链接到同一RSS源
        link2 = link_service.add_link(
            rss_source_id=rss1.id,
            url="magnet:?xt=hash1",
            link_type="magnet",
            episode_title="重复链接测试"
        )
        print(f"   再次添加相同URL链接: {link2.url} (ID: {link2.id})")
        
        if link1.id == link2.id:
            print("   ✓ 链接重复添加被正确阻止")
        else:
            print("   ✗ 链接重复添加未被阻止")
            return False
        
        print("\n4. 测试不同动画下RSS源URL可以重复...")
        # 创建另一个动画
        anime3 = anime_service.create_anime(
            title="测试动画2",
            source_url="https://example.com/anime2"
        )
        print(f"   创建第二个动画: {anime3.title} (ID: {anime3.id})")
        
        # 尝试添加相同URL的RSS源到不同的动画
        rss3 = rss_service.create_rss_source(
            anime_id=anime3.id,
            name="RSS源1 - 在不同动画中",
            url="https://example.com/rss1"
        )
        print(f"   在不同动画中添加相同URL RSS源: {rss3.name} (ID: {rss3.id})")
        
        if rss1.id != rss3.id:
            print("   ✓ 不同动画下的相同RSS源URL被正确允许")
        else:
            print("   ✗ 不同动画下的相同RSS源URL被错误阻止")
            return False
        
        print("\n5. 测试不同RSS源下链接URL可以重复...")
        # 创建另一个RSS源
        rss4 = rss_service.create_rss_source(
            anime_id=anime1.id,
            name="RSS源2",
            url="https://example.com/rss2"
        )
        print(f"   创建第二个RSS源: {rss4.name} (ID: {rss4.id})")
        
        # 尝试添加相同URL的链接到不同的RSS源
        link3 = link_service.add_link(
            rss_source_id=rss4.id,
            url="magnet:?xt=hash1",
            link_type="magnet",
            episode_title="不同RSS下的相同链接"
        )
        print(f"   在不同RSS源中添加相同URL链接: {link3.url} (ID: {link3.id})")
        
        if link1.id != link3.id:
            print("   ✓ 不同RSS源下的相同链接URL被正确允许")
        else:
            print("   ✗ 不同RSS源下的相同链接URL被错误阻止")
            return False
        
        print("\n" + "=" * 60)
        print("[成功] 所有重复添加预防测试通过")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"[错误] 测试过程中出现异常: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # 关闭数据库连接
        db.close()
        # 删除临时数据库文件
        if os.path.exists(temp_db_path):
            os.remove(temp_db_path)


if __name__ == '__main__':
    success = test_duplicate_prevention()
    sys.exit(0 if success else 1)
