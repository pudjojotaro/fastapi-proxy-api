from typing import Tuple

def construct_proxy_url(proxy: Tuple) -> str:
    """Construct a proxy URL from proxy data"""
    protocol, username, password, ip, port = proxy[1], proxy[2], proxy[3], proxy[4], proxy[5]
    if username and password:
        return f"{protocol}://{username}:{password}@{ip}:{port}"
    return f"{protocol}://{ip}:{port}"

def unlock_all_proxies():
    """Unlock all proxies in the database"""
    from .database import get_all_proxy_ids, update_proxy_status
    proxy_ids = get_all_proxy_ids()
    if proxy_ids:
        for proxy_id in proxy_ids:
            update_proxy_status(proxy_id, "available") 