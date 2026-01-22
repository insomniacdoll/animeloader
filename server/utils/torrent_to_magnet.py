"""
Torrent到Magnet链接转换工具
"""
import hashlib
import requests
from urllib.parse import urlencode
import bencodepy


def torrent_url_to_magnet(torrent_url: str) -> str:
    """
    将torrent URL转换为magnet链接
    通过下载torrent文件并提取其中的info hash来生成magnet链接
    """
    try:
        # 下载torrent文件内容
        response = requests.get(torrent_url)
        response.raise_for_status()
        
        # 解析torrent文件内容
        torrent_data = bencodepy.decode(response.content)
        
        # 提取info字典
        info = torrent_data[b'info']
        
        # 计算info hash
        info_encoded = bencodepy.encode(info)
        info_hash = hashlib.sha1(info_encoded).digest()
        
        # 将info hash转换为十六进制字符串
        info_hash_hex = info_hash.hex()
        
        # 构造magnet链接
        magnet_link = f"magnet:?xt=urn:btih:{info_hash_hex}"
        
        return magnet_link
    except Exception as e:
        print(f"转换torrent到magnet时出错: {e}")
        return None


def torrent_file_to_magnet(torrent_file_path: str) -> str:
    """
    将本地torrent文件转换为magnet链接
    """
    try:
        # 读取torrent文件
        with open(torrent_file_path, 'rb') as f:
            torrent_data = f.read()
        
        # 解析torrent文件内容
        decoded_data = bencodepy.decode(torrent_data)
        
        # 提取info字典
        info = decoded_data[b'info']
        
        # 计算info hash
        info_encoded = bencodepy.encode(info)
        info_hash = hashlib.sha1(info_encoded).digest()
        
        # 将info hash转换为十六进制字符串
        info_hash_hex = info_hash.hex()
        
        # 构造magnet链接
        magnet_link = f"magnet:?xt=urn:btih:{info_hash_hex}"
        
        return magnet_link
    except Exception as e:
        print(f"转换torrent文件到magnet时出错: {e}")
        return None