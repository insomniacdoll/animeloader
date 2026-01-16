import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server.database import init_database
from server.utils import setup_logger, config


def main():
    logger = setup_logger(
        name='animeloader',
        log_file=config.get('logging.file', './logs/animeloader.log'),
        level=config.get('logging.level', 'INFO')
    )
    
    logger.info("Initializing AnimeLoader server...")
    
    try:
        init_database()
        logger.info("Database initialized successfully")
        
        host = config.get('server.host', '127.0.0.1')
        port = config.get('server.port', 8000)
        
        logger.info(f"AnimeLoader server is ready (API server not yet implemented)")
        logger.info(f"Server would listen on {host}:{port}")
        
        print("AnimeLoader server initialized successfully!")
        print("Note: API server implementation is pending")
        
    except Exception as e:
        logger.error(f"Failed to initialize server: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()