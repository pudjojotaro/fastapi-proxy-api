import sqlite3
import logging
from fastapi import HTTPException
from typing import List, Optional, Tuple

logger = logging.getLogger(__name__)
db_path = "proxies.db"

def init_db():
    """Initialize the database with required tables"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS proxies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            protocol TEXT NOT NULL,
            username TEXT,
            password TEXT,
            ip TEXT NOT NULL,
            port INTEGER NOT NULL,
            status TEXT DEFAULT 'available',
            last_tested TIMESTAMP,
            fail_count INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def get_all_proxy_ids() -> List[int]:
    """Get all proxy IDs from the database"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM proxies")
    proxy_ids = [row[0] for row in cursor.fetchall()]
    conn.close()
    return proxy_ids

def get_proxy_by_id(proxy_id: int) -> Optional[Tuple]:
    """Get a proxy by its ID"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM proxies WHERE id = ?', (proxy_id,))
    proxy = cursor.fetchone()
    conn.close()
    return proxy

def update_proxy_status(proxy_id: int, status: str):
    """Update the status of a proxy"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE proxies
        SET status = ?, last_tested = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (status, proxy_id))
    conn.commit()
    conn.close()

def get_all_available_proxies():
    """Get all available proxies from the database"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            SELECT * FROM proxies 
            WHERE status = 'available'
        ''')
        available_proxies = cursor.fetchall()
        return available_proxies
    except Exception as e:
        logger.error(f"Error getting available proxies: {e}")
        raise HTTPException(status_code=500, detail="Failed to get available proxies")

def add_proxy_to_db(protocol: str, ip: str, port: int, username: Optional[str], password: Optional[str]):
    """Add a new proxy to the database"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO proxies (protocol, username, password, ip, port)
            VALUES (?, ?, ?, ?, ?)
        ''', (protocol, username, password, ip, port))
        conn.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Proxy already exists")
    finally:
        conn.close()

def clear_unused_proxies() -> int:
    """Clear all proxies that are not locked and return count of deleted entries"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            DELETE FROM proxies 
            WHERE status != 'locked'
        ''')
        deleted_count = cursor.rowcount
        conn.commit()
        logger.info(f"Cleared {deleted_count} unused proxies from database")
        return deleted_count
    except Exception as e:
        logger.error(f"Error clearing unused proxies: {e}")
        raise HTTPException(status_code=500, detail="Failed to clear unused proxies")
    finally:
        conn.close()