import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cmd2
from client.api import APIClient


class AnimeLoaderCLI(cmd2.Cmd):
    intro = 'AnimeLoader CLI - 动画加载器命令行工具\n输入 help 或 ? 查看可用命令。\n'
    prompt = 'animeloader> '
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api_client = APIClient()
    
    def do_anime(self, args):
        """动画相关命令"""
        self.poutput("动画命令尚未实现")
    
    def do_rss(self, args):
        """RSS源相关命令"""
        self.poutput("RSS命令尚未实现")
    
    def do_link(self, args):
        """链接相关命令"""
        self.poutput("链接命令尚未实现")
    
    def do_downloader(self, args):
        """下载器相关命令"""
        self.poutput("下载器命令尚未实现")
    
    def do_download(self, args):
        """下载相关命令"""
        self.poutput("下载命令尚未实现")
    
    def do_status(self, args):
        """状态查询命令"""
        self.poutput("状态命令尚未实现")
    
    def do_exit(self, args):
        """退出程序"""
        self.poutput("再见！")
        return True
    
    def do_quit(self, args):
        """退出程序"""
        return self.do_exit(args)


def main():
    print("AnimeLoader CLI - 动画加载器命令行工具")
    print("注意: 服务端API尚未实现，当前仅提供CLI框架")
    print()
    
    cli = AnimeLoaderCLI()
    cli.cmdloop()


if __name__ == '__main__':
    main()