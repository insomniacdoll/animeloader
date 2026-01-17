from server.database.session import get_engine, get_session_local, get_db, init_database

# 为了兼容性，提供变量访问
engine = get_engine
SessionLocal = get_session_local

__all__ = [
    'get_engine',
    'get_session_local',
    'get_db',
    'init_database',
    'engine',
    'SessionLocal',
]