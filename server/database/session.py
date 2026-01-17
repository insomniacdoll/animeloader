from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import os


# 全局变量，延迟初始化
_engine = None
_SessionLocal = None


def get_database_url() -> str:
    """从配置文件获取数据库 URL"""
    from server.utils.config import config
    
    # 获取数据库路径配置，默认为 ~/.animeloader/data/animeloader.db
    db_path = config.get_path('database.path', '~/.animeloader/data/animeloader.db')
    
    # 确保数据库目录存在
    db_dir = os.path.dirname(db_path)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
    
    return f"sqlite:///{db_path}"


def get_engine():
    """获取数据库引擎（延迟初始化）"""
    global _engine
    if _engine is None:
        _engine = create_engine(get_database_url(), echo=False)
    return _engine


def get_session_local():
    """获取 SessionLocal 工厂（延迟初始化）"""
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())
    return _SessionLocal


# 为了兼容性，提供属性访问
@property
def engine():
    return get_engine()


@property
def SessionLocal():
    return get_session_local()


def get_db() -> Session:
    """获取数据库会话"""
    SessionLocal = get_session_local()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_database():
    """初始化数据库"""
    from server.models import Base
    engine = get_engine()
    Base.metadata.create_all(bind=engine)


# 导出函数供外部使用
__all__ = [
    'get_engine',
    'get_session_local',
    'get_db',
    'init_database',
]