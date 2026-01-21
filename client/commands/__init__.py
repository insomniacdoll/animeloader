# -*- coding: utf-8 -*-
# CLI 命令模块

from .anime_commands import AnimeCommands
from .rss_commands import RSSCommands
from .link_commands import LinkCommands
from .downloader_commands import DownloaderCommands
from .download_commands import DownloadCommands
from .status_commands import StatusCommands

__all__ = [
    'AnimeCommands',
    'RSSCommands',
    'LinkCommands',
    'DownloaderCommands',
    'DownloadCommands',
    'StatusCommands'
]