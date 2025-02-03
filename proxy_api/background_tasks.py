import asyncio
from datetime import datetime, timedelta
from .utils import clear_and_repopulate_db
import logging

logger = logging.getLogger(__name__)

async def periodic_refresh():
    """Run proxy refresh every 24 hours"""
    while True:
        try:
            logger.info("Starting scheduled proxy refresh")
            cleared_count = clear_and_repopulate_db()
            logger.info(f"Scheduled refresh completed. Cleared {cleared_count} proxies")
            
            # Wait for 24 hours
            await asyncio.sleep(24 * 60 * 60)  # 24 hours in seconds
            
        except Exception as e:
            logger.error(f"Error in periodic refresh: {e}")
            # Wait for 5 minutes before retrying if there's an error
            await asyncio.sleep(300) 