import sys
import os
import signal
import argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server.database import init_database
from server.utils import setup_logger, config, init_config
from server.api.routes import router


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='AnimeLoader Server - 动画下载管理服务端'
    )
    parser.add_argument(
        '--config',
        type=str,
        default=None,
        help='配置文件路径（默认：~/.animeloader/server_config.yaml）'
    )
    return parser.parse_args()


class AnimeLoaderServer:
    def __init__(self, config_instance=None):
        # 使用传入的配置实例或全局配置
        self.config = config_instance if config_instance is not None else config
        
        self.logger = setup_logger(
            name='animeloader',
            log_file=self.config.get_path('logging.file', '~/.animeloader/logs/animeloader.log') if self.config else '~/.animeloader/logs/animeloader.log',
            level=self.config.get('logging.level', 'INFO') if self.config else 'INFO'
        )
        self.running = False
        self.app = None
        
        # 注册信号处理
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        self.logger.info(f"Received signal {signum}, shutting down...")
        self.stop()
    
    def initialize(self) -> bool:
        try:
            self.logger.info("Initializing AnimeLoader server...")
            
            # 初始化数据库
            init_database()
            self.logger.info("Database initialized successfully")
            
            # 初始化FastAPI应用
            from fastapi import FastAPI
            from fastapi.middleware.cors import CORSMiddleware
            
            self.app = FastAPI(
                title="AnimeLoader API",
                description="动画下载管理服务端API",
                version="0.1.0"
            )
            
            # 添加CORS中间件
            self.app.add_middleware(
                CORSMiddleware,
                allow_origins=["*"],
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )
            
            # 注册路由
            self.app.include_router(router)
            
            self.logger.info("FastAPI application initialized")
            
            # TODO: 初始化调度器
            scheduler_enabled = self.config.get('scheduler.enabled', True) if self.config else True
            if scheduler_enabled:
                self.logger.info("Scheduler is enabled (implementation pending)")
            
            # TODO: 初始化下载器管理器
            self.logger.info("Downloader manager initialization (implementation pending)")
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize server: {e}")
            return False
    
    def start(self):
        if not self.initialize():
            sys.exit(1)
        
        host = self.config.get('server.host', '127.0.0.1') if self.config else '127.0.0.1'
        port = self.config.get('server.port', 8000) if self.config else 8000
        debug = self.config.get('server.debug', False) if self.config else False
        
        self.logger.info(f"AnimeLoader server is ready")
        self.logger.info(f"Server listening on {host}:{port}")
        self.logger.info(f"Debug mode: {debug}")
        
        print("=" * 50)
        print("AnimeLoader Server")
        print("=" * 50)
        print(f"Host: {host}")
        print(f"Port: {port}")
        print(f"Debug: {debug}")
        print("=" * 50)
        print("API Documentation:")
        print(f"  - Swagger UI: http://{host}:{port}/docs")
        print(f"  - ReDoc: http://{host}:{port}/redoc")
        print("=" * 50)
        print("Press Ctrl+C to stop the server")
        print("=" * 50)
        
        self.running = True
        
        try:
            import uvicorn
            uvicorn.run(
                self.app,
                host=host,
                port=port,
                log_level="info" if debug else "warning"
            )
        except KeyboardInterrupt:
            self.logger.info("Keyboard interrupt received")
        finally:
            self.stop()
    
    def stop(self):
        if self.running:
            self.logger.info("Stopping AnimeLoader server...")
            self.running = False
            # TODO: 停止调度器
            self.logger.info("AnimeLoader server stopped")


def main():
    # 解析命令行参数
    args = parse_args()
    
    # 初始化配置
    config_instance = init_config(args.config)
    
    # 启动服务器
    server = AnimeLoaderServer(config_instance)
    server.start()


if __name__ == '__main__':
    main()