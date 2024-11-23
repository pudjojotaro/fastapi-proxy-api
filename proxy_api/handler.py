from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.security.api_key import APIKeyHeader
from typing import Optional, List
import logging
import os
from dotenv import load_dotenv
from .database import (
    init_db, get_proxy_by_id, update_proxy_status,
    get_all_available_proxies, add_proxy_to_db
)
from .utils import construct_proxy_url, unlock_all_proxies
from .background import check_proxies
from .proxy_converter import convert_proxies

# Initialize logging and load environment variables
load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI()

# API Key setup
API_KEY = os.getenv("API_KEY", "your-default-api-key")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def verify_api_key(api_key: str = Depends(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Forbidden")

# Route definitions
@app.post("/add_proxy", dependencies=[Depends(verify_api_key)])
def add_proxy(
    protocol: str,
    ip: str,
    port: int,
    username: Optional[str] = None,
    password: Optional[str] = None
):
    add_proxy_to_db(protocol, ip, port, username, password)
    logger.info(f"Added proxy: {protocol}://{username}:{password}@{ip}:{port}")
    return {"message": "Proxy added successfully"}

@app.get("/test_proxy/{proxy_id}", dependencies=[Depends(verify_api_key)])
def test_proxy(proxy_id: int):
    proxy = get_proxy_by_id(proxy_id)
    if not proxy:
        raise HTTPException(status_code=404, detail="Proxy not found")
    
    proxy_url = construct_proxy_url(proxy)
    try:
        import requests
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

@app.get("/get_proxies", dependencies=[Depends(verify_api_key)])
def get_proxies(count: int = 1):
    proxies = get_all_available_proxies()[:count]
    if not proxies:
        raise HTTPException(status_code=404, detail="No available proxies")
    
    result = []
    for proxy in proxies:
        proxy_id = proxy[0]
        constructed_proxy = construct_proxy_url(proxy)
        result.append({"id": proxy_id, "proxy": constructed_proxy})
        update_proxy_status(proxy_id, "locked")
    
    return {"proxies": result}

@app.post("/unlock_proxies", dependencies=[Depends(verify_api_key)])
async def unlock_proxies_endpoint(proxy_ids: List[int]):
    for proxy_id in proxy_ids:
        update_proxy_status(proxy_id, "available")
    logger.info(f"Unlocked proxies: {proxy_ids}")
    return {"message": "Proxies unlocked successfully"}

@app.get("/available_proxies", response_model=List[dict])
async def available_proxies(auto_lock: bool = True):
    proxies = get_all_available_proxies()
    if not proxies:
        logger.info("No available proxies found")
        return []
    
    formatted_proxies = []
    proxy_ids = []
    for proxy in proxies:
        proxy_id = proxy[0]
        proxy_ids.append(proxy_id)
        formatted_proxy = {
            "id": proxy_id,
            "protocol": proxy[1],
            "username": proxy[2],
            "password": proxy[3],
            "ip": proxy[4],
            "port": proxy[5],
            "status": proxy[6],
            "last_tested": proxy[7],
            "fail_count": proxy[8]
        }
        formatted_proxies.append(formatted_proxy)
    
    if auto_lock and proxy_ids:
        for proxy_id in proxy_ids:
            update_proxy_status(proxy_id, "locked")
        logger.info(f"Locked {len(proxy_ids)} proxies: {proxy_ids}")
    
    return formatted_proxies

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    init_db()
    convert_proxies()
    unlock_all_proxies()
    background_tasks = BackgroundTasks()
    background_tasks.add_task(check_proxies)

@app.on_event("shutdown")
async def shutdown_event():
    unlock_all_proxies()