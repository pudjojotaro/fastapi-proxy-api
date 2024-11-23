import asyncio
import logging
import requests
from .database import update_proxy_status
from .utils import construct_proxy_url

logger = logging.getLogger(__name__)

async def check_proxies():
    """Background task to check proxies periodically"""
    while True:
        from .database import db_path
        import sqlite3
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM proxies
            WHERE status != 'locked'
        ''')
        proxies = cursor.fetchall()
        conn.close()

        for proxy in proxies:
            proxy_id = proxy[0]
            proxy_url = construct_proxy_url(proxy)
            try:
                response = requests.get(
                    "https://httpbin.org/ip",
                    proxies={"http": proxy_url, "https": proxy_url},
                    timeout=5
                )
                response.raise_for_status()
                update_proxy_status(proxy_id, "available")
                logger.info(f"Background check: Proxy {proxy_id} is available")
            except Exception as e:
                update_proxy_status(proxy_id, "inactive")
                logger.warning(f"Background check: Proxy {proxy_id} failed: {e}")
        
        await asyncio.sleep(3600)  # Run every 1 hour 