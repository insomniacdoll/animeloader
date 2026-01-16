import sys
import os
import signal

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server.database import init_database
from server.utils import setup_logger, config


class AnimeLoaderServer:
    def __init__(self):
        self.logger = setup_logger(
            name='animeloader',
            log_file=config.get('logging.file', './logs/animeloader.log'),
            level=config.get('logging.level', 'INFO')
        )
        self.running = False
        
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
            
            # TODO: 初始化调度器
            scheduler_enabled = config.get('scheduler.enabled', True)
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
        
        host = config.get('server.host', '127.0.0.1')
        port = config.get('server.port', 8000)
        debug = config.get('server.debug', False)
        
        self.logger.info(f"AnimeLoader server is ready")
        self.logger.info(f"Server would listen on {host}:{port}")
        self.logger.info(f"Debug mode: {debug}")
        
        print("=" * 50)
        print("AnimeLoader Server")
        print("=" * 50)
        print(f"Host: {host}")
        print(f"Port: {port}")
        print(f"Debug: {debug}")
        print("=" * 50)
        print("Note: API server implementation is pending")
        print("Press Ctrl+C to stop the server")
        print("=" * 50)
        
        self.running = True
        
        try:
            while self.running:
                # TODO: 启动 API 服务器
                # TODO: 启动调度器
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            self.logger.info("Keyboard interrupt received")
        finally:
            self.stop()
    
    def stop(self):
        if self.running:
            self.logger.info("Stopping AnimeLoader server...")
            self.running = False
            # TODO: 停止调度器
            # TODO: 停止 API 服务器
            self.logger.info("AnimeLoader server stopped")


def main():
    server = AnimeLoaderServer()
    server.start()


if __name__ == '__main__':
    main()