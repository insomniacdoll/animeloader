import re
from typing import Dict, Any
from server.parsers.base_parser import BaseParser


class MagnetParser(BaseParser):
    def parse(self, url: str) -> Dict[str, Any]:
        """解析磁力链接，返回链接元数据"""
        result = {
            'file_size': 0,
            'filename': '',
            'info_hash': '',
        }
        
        if not url.startswith('magnet:?'):
            return result
        
        params = url.split('?')[1]
        param_dict = {}
        for param in params.split('&'):
            if '=' in param:
                key, value = param.split('=', 1)
                param_dict[key] = value
        
        if 'xt' in param_dict:
            xt = param_dict['xt']
            if xt.startswith('urn:btih:'):
                result['info_hash'] = xt[9:]
        
        if 'dn' in param_dict:
            result['filename'] = param_dict['dn']
        
        if 'xl' in param_dict:
            try:
                result['file_size'] = int(param_dict['xl'])
            except ValueError:
                pass
        
        return result

    def validate(self, url: str) -> bool:
        """验证磁力链接格式是否正确"""
        if not url.startswith('magnet:?'):
            return False
        
        params = url.split('?')[1]
        if 'xt=urn:btih:' not in params:
            return False
        
        return True

    def get_download_command(self, url: str, save_path: str) -> str:
        """获取下载命令"""
        return f"aria2c --dir={save_path} '{url}'"