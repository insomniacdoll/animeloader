import os
import yaml
from typing import Dict, Any
from pathlib import Path


class ClientConfig:
    def __init__(self, config_path: str = None):
        self.config_path = self._resolve_config_path(config_path)
        self.config = self._load_config()
    
    def _resolve_config_path(self, config_path: str = None) -> str:
        if config_path:
            return config_path
        
        # 默认配置路径：~/.animeloader/client_config.yaml
        home_dir = Path.home()
        default_config = home_dir / '.animeloader' / 'client_config.yaml'
        
        if default_config.exists():
            return str(default_config)
        
        # 如果默认配置不存在，返回项目目录下的配置文件
        project_root = Path(__file__).parent.parent.parent
        return str(project_root / 'client_config.yaml')
    
    def _load_config(self) -> Dict[str, Any]:
        if not os.path.exists(self.config_path):
            # 返回默认配置
            config = self._get_default_config()
        else:
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    loaded_config = yaml.safe_load(f) or {}
                    # 合并默认配置
                    default_config = self._get_default_config()
                    config = self._merge_config(default_config, loaded_config)
            except Exception as e:
                print(f"Warning: Failed to load config from {self.config_path}: {e}")
                config = self._get_default_config()
        
        # 验证API密钥是否配置
        api_key = config.get('server', {}).get('api_key', '')
        if not api_key or api_key.strip() == '':
            print("=" * 60)
            print("错误: 未配置API密钥")
            print("=" * 60)
            print("客户端需要API密钥才能访问服务端API。")
            print()
            print("请按以下步骤配置API密钥:")
            print("1. 启动服务端，服务端会自动创建默认API密钥")
            print("2. 从服务端日志中复制默认API密钥")
            print("3. 在配置文件中设置 server.api_key 字段")
            print(f"   配置文件路径: {self.config_path}")
            print()
            print("配置示例:")
            print("server:")
            print("  url: \"http://127.0.0.1:8000\"")
            print("  timeout: 30")
            print("  api_key: \"<从服务端日志中复制的API密钥>\"")
            print("=" * 60)
            raise ValueError("API密钥未配置，请在配置文件中设置 server.api_key")
        
        return config
    
    def _get_default_config(self) -> Dict[str, Any]:
        return {
            'server': {
                'url': 'http://127.0.0.1:8000',
                'timeout': 30,
                'retry_count': 3,
                'api_key': ''
            },
            'display': {
                'theme': 'auto',
                'table_max_rows': 20,
                'show_progress': True,
                'refresh_interval': 5,
                'colors': {
                    'success': 'green',
                    'error': 'red',
                    'warning': 'yellow',
                    'info': 'blue',
                    'download_speed': 'cyan',
                    'upload_speed': 'magenta'
                }
            },
            'ui': {
                'use_rich': True,
                'use_cmd2': True,
                'emoji': True,
                'compact_mode': False,
                'verbose': False,
                'cmd2': {
                    'allow_cli_args': True,
                    'shortcuts': True,
                    'persistent_history_file': '~/.animeloader/.cmd2_history'
                }
            },
            'logging': {
                'level': 'INFO',
                'file': ''
            }
        }
    
    def _merge_config(self, default: Dict[str, Any], loaded: Dict[str, Any]) -> Dict[str, Any]:
        result = default.copy()
        for key, value in loaded.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_config(result[key], value)
            else:
                result[key] = value
        return result
    
    def get(self, key: str, default: Any = None) -> Any:
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default
    
    def reload(self) -> None:
        self.config = self._load_config()


config = ClientConfig()