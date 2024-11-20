import sqlite3
import re
import logging
import os

# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Database path
db_path = "proxies.db"

# Initialize the database (ensure table exists)
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

# Parse proxy line into components
def parse_proxy(proxy_line):
    """
    Expected formats:
    - protocol://username:password@ip:port
    - protocol://ip:port
    """
    pattern = re.compile(
        r'^(http|https)://(?:([^:@]+):([^@]+)@)?(\d{1,3}(?:\.\d{1,3}){3}):(\d{2,5})$'
    )
    match = pattern.match(proxy_line.strip())
    if not match:
        logger.warning(f"Invalid proxy format: {proxy_line}")
        return None
    protocol, username, password, ip, port = match.groups()
    return {
        "protocol": protocol,
        "username": username,
        "password": password,
        "ip": ip,
        "port": int(port)
    }

# Insert proxy into the database
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

# Load proxies from proxies.txt and insert into the database
def load_proxies(file_path="proxies.txt"):
    if not os.path.exists(file_path):
        logger.error(f"Proxy file not found: {file_path}")
        return
    
    with open(file_path, 'r') as f:
        for line in f:
            proxy = parse_proxy(line)
            if proxy:
                insert_proxy(proxy)

if __name__ == "__main__":
    init_db()
    load_proxies()
    logger.info("Proxy conversion completed.")