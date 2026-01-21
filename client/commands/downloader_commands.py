import argparse
import shlex
import json
from rich.console import Console
from rich.table import Table


class DownloaderCommands:
    """下载器相关命令实现"""
    
    def __init__(self, api_client, console, config):
        self.api_client = api_client
        self.console = console
        self.config = config
    
    def add(self, args):
        """添加下载器"""
        parser = argparse.ArgumentParser(prog='downloader add', add_help=False)
        parser.add_argument('--name', required=True, help='下载器名称')
        parser.add_argument('--type', required=True, help='下载器类型 (aria2, pikpak, qbittorrent)')
        parser.add_argument('--config', required=True, help='下载器配置 (JSON格式)')
        parser.add_argument('--max-concurrent', type=int, default=3, help='最大并发任务数')
        parser.add_argument('-h', '--help', action='store_true', help='显示帮助')
        
        try:
            parsed = parser.parse_args(shlex.split(args))
            if parsed.help:
                parser.print_help()
                return
            
            # 解析配置JSON
            try:
                config_data = json.loads(parsed.config)
            except json.JSONDecodeError as e:
                self._print_error(f"配置JSON格式错误: {e}")
                return
            
            # 构建请求数据
            data = {
                'name': parsed.name,
                'downloader_type': parsed.type,
                'config': json.dumps(config_data),
                'is_active': True,
                'is_default': False,
                'max_concurrent_tasks': parsed.max_concurrent
            }
            
            # 调用API创建下载器
            response = self.api_client.post('/api/downloaders', json_data=data)
            
            if 'error' in response:
                self._print_error(f"添加下载器失败: {response['error']}")
                return
            
            downloader = response
            self._print_success(f"下载器添加成功: {downloader['name']}")
            self.console.print(f"ID: {downloader['id']}")
            self.console.print(f"类型: {downloader['downloader_type']}")
            self.console.print(f"最大并发: {downloader.get('max_concurrent_tasks', 'N/A')}")
                
        except SystemExit:
            pass
        except Exception as e:
            self._print_error(f"参数错误: {e}")
    
    def list(self, args):
        """列出下载器"""
        parser = argparse.ArgumentParser(prog='downloader list', add_help=False)
        parser.add_argument('-h', '--help', action='store_true', help='显示帮助')
        
        try:
            parsed = parser.parse_args(shlex.split(args))
            if parsed.help:
                parser.print_help()
                return
            
            # 调用API获取下载器列表
            response = self.api_client.get('/api/downloaders')
            
            if 'error' in response:
                self._print_error(f"获取下载器列表失败: {response['error']}")
                return
            
            downloaders = response if isinstance(response, list) else []
            
            if not downloaders:
                self._print_info("没有找到下载器")
                return
            
            # 显示下载器列表
            table = Table(title=f"下载器列表 (共 {len(downloaders)} 个)")
            table.add_column("ID", style="cyan", width=6)
            table.add_column("名称", style="magenta")
            table.add_column("类型", style="green")
            table.add_column("状态", style="yellow", width=6)
            table.add_column("默认", style="blue", width=6)
            table.add_column("最大并发", style="red", width=8)
            table.add_column("创建时间", style="dim", width=19)
            
            for downloader in downloaders:
                table.add_row(
                    str(downloader['id']),
                    downloader['name'],
                    downloader['downloader_type'],
                    "激活" if downloader.get('is_active') else "停用",
                    "是" if downloader.get('is_default') else "否",
                    str(downloader.get('max_concurrent_tasks', 'N/A')),
                    downloader.get('created_at', 'N/A')[:19]
                )
            
            self.console.print(table)
                
        except SystemExit:
            pass
        except Exception as e:
            self._print_error(f"参数错误: {e}")
    
    def show(self, args):
        """显示下载器详情"""
        parser = argparse.ArgumentParser(prog='downloader show', add_help=False)
        parser.add_argument('--id', type=int, required=True, help='下载器ID')
        parser.add_argument('-h', '--help', action='store_true', help='显示帮助')
        
        try:
            parsed = parser.parse_args(shlex.split(args))
            if parsed.help:
                parser.print_help()
                return
            
            # 调用API获取下载器详情
            response = self.api_client.get(f'/api/downloaders/{parsed.id}')
            
            if 'error' in response:
                self._print_error(f"获取下载器详情失败: {response['error']}")
                return
            
            downloader = response
            
            # 显示下载器详情
            table = Table(title=f"下载器详情: {downloader['name']}")
            table.add_column("属性", style="cyan")
            table.add_column("值", style="green")
            
            table.add_row("ID", str(downloader['id']))
            table.add_row("名称", downloader['name'])
            table.add_row("类型", downloader['downloader_type'])
            table.add_row("状态", "激活" if downloader.get('is_active') else "停用")
            table.add_row("默认", "是" if downloader.get('is_default') else "否")
            table.add_row("最大并发任务数", str(downloader.get('max_concurrent_tasks', 'N/A')))
            
            config_str = downloader.get('config', '{}')
            try:
                config_json = json.loads(config_str)
                table.add_row("配置", json.dumps(config_json, indent=2, ensure_ascii=False))
            except:
                table.add_row("配置", config_str)
            
            table.add_row("创建时间", downloader.get('created_at', 'N/A'))
            table.add_row("更新时间", downloader.get('updated_at', 'N/A'))
            
            self.console.print(table)
            
        except SystemExit:
            pass
        except Exception as e:
            self._print_error(f"参数错误: {e}")
    
    def update(self, args):
        """更新下载器"""
        parser = argparse.ArgumentParser(prog='downloader update', add_help=False)
        parser.add_argument('--id', type=int, required=True, help='下载器ID')
        parser.add_argument('--name', help='下载器名称')
        parser.add_argument('--config', help='下载器配置 (JSON格式)')
        parser.add_argument('--is-active', type=bool, help='是否激活')
        parser.add_argument('--max-concurrent', type=int, help='最大并发任务数')
        parser.add_argument('-h', '--help', action='store_true', help='显示帮助')
        
        try:
            parsed = parser.parse_args(shlex.split(args))
            if parsed.help:
                parser.print_help()
                return
            
            # 构建请求数据
            data = {}
            
            if parsed.name:
                data['name'] = parsed.name
            if parsed.config:
                try:
                    config_data = json.loads(parsed.config)
                    data['config'] = json.dumps(config_data)
                except json.JSONDecodeError as e:
                    self._print_error(f"配置JSON格式错误: {e}")
                    return
            if parsed.is_active is not None:
                data['is_active'] = parsed.is_active
            if parsed.max_concurrent is not None:
                data['max_concurrent_tasks'] = parsed.max_concurrent
            
            if not data:
                self._print_warning("没有提供任何更新参数")
                return
            
            # 调用API更新下载器
            response = self.api_client.put(f'/api/downloaders/{parsed.id}', json_data=data)
            
            if 'error' in response:
                self._print_error(f"更新下载器失败: {response['error']}")
                return
            
            downloader = response
            self._print_success(f"下载器更新成功: {downloader['name']}")
                
        except SystemExit:
            pass
        except Exception as e:
            self._print_error(f"参数错误: {e}")
    
    def remove(self, args):
        """删除下载器"""
        parser = argparse.ArgumentParser(prog='downloader remove', add_help=False)
        parser.add_argument('--id', type=int, required=True, help='下载器ID')
        parser.add_argument('-h', '--help', action='store_true', help='显示帮助')
        
        try:
            parsed = parser.parse_args(shlex.split(args))
            if parsed.help:
                parser.print_help()
                return
            
            # 调用API删除下载器
            response = self.api_client.delete(f'/api/downloaders/{parsed.id}')
            
            if 'error' in response:
                self._print_error(f"删除下载器失败: {response['error']}")
                return
            
            self._print_success(f"下载器删除成功 (ID: {parsed.id})")
                
        except SystemExit:
            pass
        except Exception as e:
            self._print_error(f"参数错误: {e}")
    
    def test(self, args):
        """测试下载器连接"""
        parser = argparse.ArgumentParser(prog='downloader test', add_help=False)
        parser.add_argument('--id', type=int, required=True, help='下载器ID')
        parser.add_argument('-h', '--help', action='store_true', help='显示帮助')
        
        try:
            parsed = parser.parse_args(shlex.split(args))
            if parsed.help:
                parser.print_help()
                return
            
            self.console.print(f"正在测试下载器连接 (ID: {parsed.id})...")
            
            # 调用API测试下载器
            response = self.api_client.post(f'/api/downloaders/{parsed.id}/test')
            
            if 'error' in response:
                self._print_error(f"测试失败: {response['error']}")
                return
            
            result = response
            if result.get('success'):
                self._print_success(f"下载器连接测试成功")
                if result.get('message'):
                    self.console.print(f"信息: {result['message']}")
            else:
                self._print_error(f"下载器连接测试失败")
                if result.get('message'):
                    self.console.print(f"错误: {result['message']}")
                
        except SystemExit:
            pass
        except Exception as e:
            self._print_error(f"参数错误: {e}")
    
    def set_default(self, args):
        """设置默认下载器"""
        parser = argparse.ArgumentParser(prog='downloader set-default', add_help=False)
        parser.add_argument('--id', type=int, required=True, help='下载器ID')
        parser.add_argument('-h', '--help', action='store_true', help='显示帮助')
        
        try:
            parsed = parser.parse_args(shlex.split(args))
            if parsed.help:
                parser.print_help()
                return
            
            # 调用API设置默认下载器
            response = self.api_client.post(f'/api/downloaders/{parsed.id}/set-default')
            
            if 'error' in response:
                self._print_error(f"设置默认下载器失败: {response['error']}")
                return
            
            self._print_success(f"已设置默认下载器 (ID: {parsed.id})")
                
        except SystemExit:
            pass
        except Exception as e:
            self._print_error(f"参数错误: {e}")
    
    def types(self, args):
        """查看支持的下载器类型"""
        parser = argparse.ArgumentParser(prog='downloader types', add_help=False)
        parser.add_argument('-h', '--help', action='store_true', help='显示帮助')
        
        try:
            parsed = parser.parse_args(shlex.split(args))
            if parsed.help:
                parser.print_help()
                return
            
            # 调用API获取支持的下载器类型
            response = self.api_client.get('/api/downloaders/types')
            
            if 'error' in response:
                self._print_error(f"获取下载器类型失败: {response['error']}")
                return
            
            types = response.get('types', [])
            
            if not types:
                self._print_info("没有找到支持的下载器类型")
                return
            
            # 显示下载器类型
            table = Table(title="支持的下载器类型")
            table.add_column("类型", style="cyan")
            table.add_column("描述", style="green")
            
            for downloader_type in types:
                table.add_row(
                    downloader_type.get('type', 'N/A'),
                    downloader_type.get('description', 'N/A')
                )
            
            self.console.print(table)
                
        except SystemExit:
            pass
        except Exception as e:
            self._print_error(f"参数错误: {e}")
    
    def help(self):
        """显示 downloader 命令的帮助信息"""
        help_text = """
下载器相关命令

用法: downloader <子命令> [选项]

子命令:
  add          添加下载器
  list         列出下载器
  show         显示下载器详情
  update       更新下载器
  remove       删除下载器
  test         测试下载器连接
  set-default  设置默认下载器
  types        查看支持的下载器类型

使用 'downloader <子命令> --help' 查看子命令的详细帮助
        """
        self.console.print(help_text)
    
    def _print_success(self, message: str):
        emoji = "✅ " if self.config.get('ui.emoji', True) else ""
        self.console.print(f"{emoji}{message}", style="green")
    
    def _print_error(self, message: str):
        emoji = "❌ " if self.config.get('ui.emoji', True) else ""
        self.console.print(f"{emoji}{message}", style="red")
    
    def _print_warning(self, message: str):
        emoji = "⚠️  " if self.config.get('ui.emoji', True) else ""
        self.console.print(f"{emoji}{message}", style="yellow")
    
    def _print_info(self, message: str):
        emoji = "ℹ️  " if self.config.get('ui.emoji', True) else ""
        self.console.print(f"{emoji}{message}", style="blue")