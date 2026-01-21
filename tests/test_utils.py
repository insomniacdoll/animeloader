"""
测试工具模块
提供测试隔离和临时文件管理功能
"""
import os
import sys
import tempfile
import shutil
import subprocess
import time
import signal
from pathlib import Path
from typing import Optional, Callable


class TestEnvironment:
    """测试环境管理类"""
    
    def __init__(self):
        self.temp_dir: Optional[str] = None
        self.original_cwd: Optional[str] = None
        self.config_file: Optional[str] = None
        self.log_dir: Optional[str] = None
        self.data_dir: Optional[str] = None
        self.db_file: Optional[str] = None
        self.server_process: Optional[subprocess.Popen] = None
        self.server_host: str = "127.0.0.1"
        self.server_port: int = 8000
    
    def setup(self) -> str:
        """
        设置测试环境
        
        Returns:
            临时目录路径
        """
        # 创建临时目录
        self.temp_dir = tempfile.mkdtemp(prefix='animeloader_test_')
        
        # 保存当前工作目录
        self.original_cwd = os.getcwd()
        
        # 切换到临时目录
        os.chdir(self.temp_dir)
        
        # 创建必要的目录
        self.data_dir = os.path.join(self.temp_dir, 'data')
        self.log_dir = os.path.join(self.temp_dir, 'logs')
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.log_dir, exist_ok=True)
        
        # 数据库文件路径
        self.db_file = os.path.join(self.data_dir, 'animeloader.db')
        
        # 配置文件路径
        self.config_file = os.path.join(self.temp_dir, 'server_config.yaml')
        
        # 创建测试配置文件
        self._create_config_file()
        
        # 添加项目根目录到 Python 路径
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        
        return self.temp_dir
    
    def _create_config_file(self):
        """创建测试配置文件"""
        config_content = """
server:
  host: "127.0.0.1"
  port: 8000
  debug: false

database:
  path: "{db_path}"

logging:
  level: "INFO"
  file: "{log_path}/animeloader.log"

scheduler:
  enabled: true

smart_parser:
  timeout: 30
  user_agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
  max_results: 10
  auto_add_rss: true
""".format(
            db_path=self.db_file,
            log_path=self.log_dir
        )
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            f.write(config_content)
    
    def get_config_path(self) -> str:
        """获取配置文件路径"""
        return self.config_file
    
    def get_db_path(self) -> str:
        """获取数据库文件路径"""
        return self.db_file
    
    def get_log_path(self) -> str:
        """获取日志目录路径"""
        return self.log_dir
    
    def print_info(self):
        """打印测试环境信息"""
        print("\n" + "=" * 60)
        print("测试环境信息")
        print("=" * 60)
        print(f"临时目录: {self.temp_dir}")
        print(f"配置文件: {self.config_file}")
        print(f"数据库文件: {self.db_file}")
        print(f"日志目录: {self.log_dir}")
        print(f"数据目录: {self.data_dir}")
        print(f"服务端地址: {self.get_server_url()}")
        print("=" * 60 + "\n")
    
    def get_server_url(self) -> str:
        """获取服务端 URL"""
        return f"http://{self.server_host}:{self.server_port}"
    
    def start_server(self, timeout: int = 10) -> bool:
        """
        启动服务端进程
        
        Args:
            timeout: 等待服务端启动的超时时间（秒）
            
        Returns:
            是否成功启动
        """
        if self.server_process is not None:
            print("服务端已经在运行")
            return True
        
        print(f"启动服务端...")
        print(f"  配置文件: {self.config_file}")
        print(f"  地址: {self.get_server_url()}")
        
        # 获取 Python 解释器路径
        python_path = sys.executable
        
        # 获取项目根目录
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # 设置环境变量，确保子进程能够找到 server 模块
        env = os.environ.copy()
        if 'PYTHONPATH' in env:
            env['PYTHONPATH'] = f"{project_root}:{env['PYTHONPATH']}"
        else:
            env['PYTHONPATH'] = project_root
        
        # 启动服务端
        try:
            self.server_process = subprocess.Popen(
                [python_path, "-m", "server.main", "--config", self.config_file],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env
            )
            
            # 等待服务端启动
            start_time = time.time()
            while time.time() - start_time < timeout:
                if self.server_process.poll() is not None:
                    # 进程已经退出
                    stdout, stderr = self.server_process.communicate()
                    print(f"服务端启动失败:")
                    print(f"  stdout: {stdout}")
                    print(f"  stderr: {stderr}")
                    self.server_process = None
                    return False
                
                # 尝试连接服务端
                if self._check_server_health():
                    print(f"✓ 服务端启动成功 ({self.get_server_url()})")
                    time.sleep(1)  # 额外等待确保完全启动
                    return True
                
                time.sleep(0.5)
            
            # 超时
            print(f"服务端启动超时（{timeout}秒）")
            self.stop_server()
            return False
            
        except Exception as e:
            print(f"启动服务端时发生异常: {e}")
            self.server_process = None
            return False
    
    def _check_server_health(self) -> bool:
        """检查服务端健康状态"""
        try:
            import requests
            response = requests.get(
                f"{self.get_server_url()}/api/health",
                timeout=2
            )
            return response.status_code == 200
        except:
            return False
    
    def stop_server(self):
        """停止服务端进程"""
        if self.server_process is None:
            return
        
        print("停止服务端...")
        
        try:
            # 尝试优雅地终止进程
            self.server_process.terminate()
            
            # 等待进程退出
            try:
                self.server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                # 强制杀死进程
                self.server_process.kill()
                self.server_process.wait(timeout=2)
            
            # 清理端口占用（确保端口被释放）
            self._cleanup_port()
            
            print("✓ 服务端已停止")
            
        except Exception as e:
            print(f"停止服务端时发生异常: {e}")
            # 尝试强制清理端口
            self._cleanup_port()
        finally:
            self.server_process = None
    
    def _cleanup_port(self):
        """清理端口占用"""
        try:
            # 使用 lsof 查找占用端口的进程并杀死
            subprocess.run(
                f"lsof -ti:{self.server_port} | xargs kill -9 2>/dev/null || true",
                shell=True,
                timeout=5
            )
        except:
            pass
    
    def teardown(self):
        """清理测试环境"""
        # 停止服务端进程
        self.stop_server()
        
        # 恢复原始工作目录
        if self.original_cwd:
            os.chdir(self.original_cwd)
        
        # 删除临时目录
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        
        # 清理属性
        self.temp_dir = None
        self.original_cwd = None
        self.config_file = None
        self.log_dir = None
        self.data_dir = None
        self.db_file = None
    
    def __enter__(self):
        """支持 with 语句"""
        self.setup()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """支持 with 语句"""
        self.teardown()


def run_in_test_environment(test_func: Callable) -> Callable:
    """
    装饰器：在测试环境中运行测试函数
    
    Args:
        test_func: 测试函数
        
    Returns:
        包装后的测试函数
    """
    def wrapper(*args, **kwargs):
        env = TestEnvironment()
        try:
            env.setup()
            return test_func(env, *args, **kwargs)
        finally:
            env.teardown()
    return wrapper


def get_test_config_path() -> str:
    """
    获取测试配置文件路径（用于兼容旧代码）
    
    Returns:
        配置文件路径
    """
    # 如果已经在测试环境中，返回当前环境的配置文件
    if 'TEST_ENV' in os.environ:
        return os.environ['TEST_CONFIG']
    
    # 否则，在临时目录中创建
    temp_dir = tempfile.mkdtemp(prefix='animeloader_test_')
    config_file = os.path.join(temp_dir, 'server_config.yaml')
    
    config_content = """
server:
  host: "127.0.0.1"
  port: 8000
  debug: false

database:
  path: "{db_path}"

logging:
  level: "INFO"
  file: "{log_path}/animeloader.log"

scheduler:
  enabled: true

smart_parser:
  timeout: 30
  user_agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
  max_results: 10
  auto_add_rss: true
""".format(
        db_path=os.path.join(temp_dir, 'data', 'animeloader.db'),
        log_path=os.path.join(temp_dir, 'logs')
    )
    
    os.makedirs(os.path.join(temp_dir, 'data'), exist_ok=True)
    os.makedirs(os.path.join(temp_dir, 'logs'), exist_ok=True)
    
    with open(config_file, 'w', encoding='utf-8') as f:
        f.write(config_content)
    
    os.environ['TEST_CONFIG'] = config_file
    os.environ['TEST_TEMP_DIR'] = temp_dir
    
    return config_file


def cleanup_test_environment():
    """清理测试环境"""
    if 'TEST_TEMP_DIR' in os.environ:
        temp_dir = os.environ['TEST_TEMP_DIR']
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)
        del os.environ['TEST_TEMP_DIR']
    
    if 'TEST_CONFIG' in os.environ:
        del os.environ['TEST_CONFIG']