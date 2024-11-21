import os
import sqlite3
import logging
from urllib.parse import urlparse

logger = logging.getLogger(__name__)
db_path = "proxies.db"

def parse_proxy(proxy_string):
    try:
        parsed = urlparse(proxy_string)
        protocol = parsed.scheme
        username = parsed.username
        password = parsed.password
        ip = parsed.hostname
        port = parsed.port

        return {
            'protocol': protocol,
            'username': username,
            'password': password,
            'ip': ip,
            'port': port
        }
    except Exception as e:
        logger.error(f"Failed to parse proxy: {proxy_string}, error: {e}")
        return None

def init_db():
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

def insert_proxy(proxy):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO proxies (protocol, username, password, ip, port)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            proxy['protocol'],
            proxy.get('username'),
            proxy.get('password'),
            proxy['ip'],
            proxy['port']
        ))
        conn.commit()
        logger.info(f"Inserted proxy: {proxy['protocol']}://{proxy.get('username', '')}:{proxy.get('password', '')}@{proxy['ip']}:{proxy['port']}")
    except sqlite3.IntegrityError:
        logger.warning(f"Proxy already exists: {proxy}")
    finally:
        conn.close()

def convert_proxies(file_path="proxies.txt"):
    if not os.path.exists(file_path):
        logger.error(f"Proxy file not found: {file_path}")
        return
    
    with open(file_path, 'r') as f:
        for line in f:
            proxy = parse_proxy(line.strip())
            if proxy:
                if not proxy_exists(proxy):
                    insert_proxy(proxy)
                else:
                    logger.info(f"Proxy already exists: {proxy['protocol']}://{proxy.get('username', '')}:{proxy.get('password', '')}@{proxy['ip']}:{proxy['port']}")
    logger.info("Proxy conversion completed.")

def proxy_exists(proxy):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT COUNT(*) FROM proxies
        WHERE ip = ? AND port = ? AND protocol = ?
    ''', (proxy['ip'], proxy['port'], proxy['protocol']))
    exists = cursor.fetchone()[0] > 0
    conn.close()
    return exists

if __name__ == "__main__":
    init_db()
    convert_proxies()