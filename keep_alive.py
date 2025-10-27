import os
import time
import requests
import logging
from threading import Thread

# Setup logging
logger = logging.getLogger(__name__)

def keep_alive(port=10000):
    """Pings the server periodically to prevent shutdown"""
    session = requests.Session()
    
    while True:
        try:
            # Ping our own health endpoint
            session.get(f'http://localhost:{port}/ping', timeout=5)
            logger.debug(f"Keep-alive ping sent to localhost:{port}")
        except Exception as e:
            logger.warning(f"Keep-alive ping to localhost:{port} failed: {e}")
        
        try:
            # Optionally ping external services
            session.get('https://www.google.com', timeout=5)
            logger.debug("Keep-alive ping sent to external service")
        except Exception as e:
            logger.warning(f"Keep-alive ping to external service failed: {e}")
        
        time.sleep(300)  # Ping every 5 minutes

def start_keep_alive(port=10000):
    """Start the keep-alive system in a separate thread"""
    thread = Thread(target=keep_alive, args=(port,), daemon=True)
    thread.start()
    logger.info(f"Keep-alive system started on port {port}")
    return thread