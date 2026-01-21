'''测试基类
提供通用的测试功能
'''
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server.database import init_database, get_db
from server.utils import config, init_config
from test_utils import TestEnvironment


class BaseTest:
    """测试基类"""
    
    def __init__(self, test_name: str):
        """
        初始化测试基类
        
        Args:
            test_name: 测试名称
        """
        self.test_name = test_name
        self.env = None
        self.temp_dir = None
    
    def setup(self):
        """设置测试环境"""
        print("=" * 60)
        print(f"测试: {self.test_name}")
        print("=" * 60)
        
        # 创建测试环境
        self.env = TestEnvironment()
        self.temp_dir = self.env.setup()
        
        # 打印测试环境信息
        self.env.print_info()
        
        # 初始化配置
        cfg = init_config(self.env.get_config_path())
        
        # 打印配置信息
        cfg.print_info()
        
        # 初始化数据库
        init_database()
    
    def teardown(self):
        """清理测试环境"""
        if self.env:
            self.env.teardown()
            print(f"已清理测试环境: {self.temp_dir}")
    
    def run_test(self, test_func):
        """
        运行测试函数
        
        Args:
            test_func: 测试函数
        """
        try:
            self.setup()
            test_func()
            print("\n" + "=" * 60)
            print(f"[成功] {self.test_name}测试通过")
            print("=" * 60)
        except AssertionError as e:
            print(f"\n[失败] 测试失败: {e}")
            raise
        except Exception as e:
            print(f"\n[失败] 发生错误: {e}")
            import traceback
            traceback.print_exc()
            raise
        finally:
            self.teardown()