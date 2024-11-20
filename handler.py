from fastapi import FastAPI, HTTPException, Depends
from fastapi.security.api_key import APIKeyHeader
from typing import Optional, List
from datetime import datetime
import asyncio
import sqlite3
import logging
import os

# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI()
db_path = "proxies.db"

# API Key for local security (optional)
API_KEY = os.getenv("API_KEY", "your-default-api-key")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def verify_api_key(api_key: str = Depends(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Forbidden")

# Initialize the database
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

@app.on_event("startup")
async def startup_event():
    init_db()
    asyncio.create_task(check_proxies())

# Add a new proxy (individual)
@app.post("/add_proxy", dependencies=[Depends(verify_api_key)])
def add_proxy(
    protocol: str,
    ip: str,
    port: int,
    username: Optional[str] = None,
    password: Optional[str] = None
):
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
    logger.info(f"Added proxy: {protocol}://{username}:{password}@{ip}:{port}")
    return {"message": "Proxy added successfully"}

# Test a proxy by ID
@app.get("/test_proxy/{proxy_id}", dependencies=[Depends(verify_api_key)])
def test_proxy(proxy_id: int):
    proxy = get_proxy_by_id(proxy_id)
    if not proxy:
        raise HTTPException(status_code=404, detail="Proxy not found")
    
    proxy_url = construct_proxy_url(proxy)
    try:
        import requests  # Import here to avoid issues with async
        response = requests.get(
            "https://httpbin.org/ip",
            proxies={"http": proxy_url, "https": proxy_url},
            timeout=5
        )
        response.raise_for_status()
        update_proxy_status(proxy_id, "available")
        logger.info(f"Proxy {proxy_id} is working")
        return {"message": "Proxy is working"}
    except Exception as e:
        update_proxy_status(proxy_id, "inactive")
        logger.warning(f"Proxy {proxy_id} failed: {e}")
        return {"message": "Proxy failed"}

# Update proxy status by ID
def update_proxy_status(proxy_id: int, status: str):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE proxies
        SET status = ?, last_tested = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (status, proxy_id))
    conn.commit()
    conn.close()

# Get proxy by ID
def get_proxy_by_id(proxy_id: int):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM proxies WHERE id = ?', (proxy_id,))
    proxy = cursor.fetchone()
    conn.close()
    return proxy

# Construct proxy URL
def construct_proxy_url(proxy):
    protocol, username, password, ip, port = proxy[1], proxy[2], proxy[3], proxy[4], proxy[5]
    if username and password:
        return f"{protocol}://{username}:{password}@{ip}:{port}"
    else:
        return f"{protocol}://{ip}:{port}"

# Get multiple proxies
@app.get("/get_proxies", dependencies=[Depends(verify_api_key)])
def get_proxies(count: int = 1, format: str = "http://{username}:{password}@{ip}:{port}"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM proxies
        WHERE status = 'available'
        LIMIT ?
    ''', (count,))
    results = cursor.fetchall()
    conn.close()
    
    if not results:
        raise HTTPException(status_code=404, detail="No available proxies")
    
    proxies = []
    for proxy in results:
        proxy_id = proxy[0]
        constructed_proxy = construct_proxy_url(proxy)
        proxies.append({"id": proxy_id, "proxy": constructed_proxy})
        update_proxy_status(proxy_id, "locked")
    
    return {"proxies": proxies}

# Unlock proxies by IDs
@app.post("/unlock_proxies", dependencies=[Depends(verify_api_key)])
def unlock_proxies(proxies: List[int]):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    for proxy_id in proxies:
        cursor.execute('''
            UPDATE proxies
            SET status = 'available'
            WHERE id = ?
        ''', (proxy_id,))
    conn.commit()
    conn.close()
    logger.info(f"Unlocked proxies: {proxies}")
    return {"message": "Proxies unlocked successfully"}

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Background task to check proxies periodically
async def check_proxies():
    import requests  # Imported here to avoid issues with async
    while True:
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
            protocol, username, password, ip, port = proxy[1], proxy[2], proxy[3], proxy[4], proxy[5]
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
        
        await asyncio.sleep(300)  # Run every 5 minutes