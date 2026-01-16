import re
from typing import Dict, Any
from server.parsers.base_parser import BaseParser


class Ed2kParser(BaseParser):
    def parse(self, url: str) -> Dict[str, Any]:
        """解析ed2k链接，返回链接元数据"""
        result = {
            'file_size': 0,
            'filename': '',
            'file_hash': '',
        }
        
        if not url.startswith('ed2k://'):
            return result
        
        match = re.match(r'ed2k://\|file\|(.+?)\|(\d+)\|([a-fA-F0-9]{32})\|', url)
        if match:
            result['filename'] = match.group(1)
            try:
                result['file_size'] = int(match.group(2))
            except ValueError:
                pass
            result['file_hash'] = match.group(3).lower()
        
        return result

    def validate(self, url: str) -> bool:
        """验证ed2k链接格式是否正确"""
        if not url.startswith('ed2k://'):
            return False
        
        match = re.match(r'ed2k://\|file\|(.+?)\|(\d+)\|([a-fA-F0-9]{32})\|', url)
        return match is not None

    def get_download_command(self, url: str, save_path: str) -> str:
        """获取下载命令"""
        return f"aria2c --dir={save_path} '{url}'"