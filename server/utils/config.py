import os
import yaml
from typing import Dict, Any, Optional


class Config:
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        # 配置文件加载优先级：
        # 1. 命令行参数指定的配置文件路径
        # 2. ~/.animeloader/server_config.yaml
        # 3. server_config.yaml（相对于项目根目录，仅用于开发环境）
        
        config_paths = []
        
        # 1. 命令行参数指定的配置文件
        if self.config_path:
            config_paths.append(self.config_path)
        
        # 2. 用户主目录下的配置文件
        user_config = os.path.expanduser('~/.animeloader/server_config.yaml')
        config_paths.append(user_config)
        
        # 3. 项目目录下的配置文件（仅用于开发环境）
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        dev_config = os.path.join(project_root, 'server_config.yaml')
        config_paths.append(dev_config)
        
        # 按优先级尝试加载配置文件
        for path in config_paths:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f) or {}
        
        # 如果没有找到任何配置文件，返回空字典
        return {}
    
    def _expand_path(self, path: str) -> str:
        """展开路径中的 ~ 和环境变量"""
        if path:
            return os.path.expandvars(os.path.expanduser(path))
        return path
    
    def get(self, key: str, default: Any = None) -> Any:
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default
    
    def get_path(self, key: str, default: str = None) -> str:
        """获取路径配置，自动展开 ~ 和环境变量"""
        path = self.get(key, default)
        return self._expand_path(path) if path else default
    
    def reload(self) -> None:
        self.config = self._load_config()
    
    def print_info(self):
        """打印当前配置信息"""
        print("\n" + "=" * 60)
        print("当前配置信息")
        print("=" * 60)
        print(f"配置文件: {self.config_path}")
        print(f"服务端地址: {self.get('server.host')}:{self.get('server.port')}")
        print(f"数据库路径: {self.get_path('database.path')}")
        print(f"日志文件: {self.get_path('logging.file')}")
        print(f"日志级别: {self.get('logging.level')}")
        print(f"调度器启用: {self.get('scheduler.enabled')}")
        print("=" * 60 + "\n")


# 全局配置实例（将在 main() 中初始化）
config: Optional[Config] = None


def init_config(config_path: Optional[str] = None) -> Config:
    """初始化全局配置"""
    global config
    config = Config(config_path)
    return config