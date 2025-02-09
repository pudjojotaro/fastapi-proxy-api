import requests
import os
from typing import List, Optional, Union, overload
import sqlite3

db_path = "proxies.db"

class ProxyAPI:
    def __init__(self, api_key: str = None, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.api_key = api_key or os.getenv("API_KEY", "your-default-api-key")
        self.headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }

    def add_proxy(self, protocol: str, ip: str, port: int, username: Optional[str] = None, password: Optional[str] = None) -> dict:
        url = f"{self.base_url}/add_proxy"
        data = {
            "protocol": protocol,
            "ip": ip,
            "port": port,
            "username": username,
            "password": password
        }
        response = requests.post(url, headers=self.headers, json=data)
        return response.json()

    def test_proxy(self, proxy_id: int) -> dict:
        url = f"{self.base_url}/test_proxy/{proxy_id}"
        response = requests.get(url, headers=self.headers)
        return response.json()

    def get_proxies(self, count: int = 1) -> dict:
        url = f"{self.base_url}/get_proxies"
        params = {"count": count}
        response = requests.get(url, headers=self.headers, params=params)
        return response.json()

    @overload
    def unlock_proxies(self, proxy_ids: List[int]) -> dict:
        ...

    @overload
    def unlock_proxies(self, ip: str) -> dict:
        ...

    @overload
    def unlock_proxies(self, full_address: str) -> dict:
        ...

    def unlock_proxies(self, proxies: Union[List[int], str]) -> dict:
        url = f"{self.base_url}/unlock_proxies"
        
        if isinstance(proxies, list):
            print(f"Unlocking proxies with IDs: {proxies}")  # Debugging line
            response = requests.post(url, headers=self.headers, json=proxies)  # Send the list directly
        elif isinstance(proxies, str):
            # Assuming you have a way to convert IP or full address to IDs
            proxy_ids = self.get_proxy_ids(proxies)  # Implement this method
            print(f"Unlocking proxies with IDs derived from {proxies}: {proxy_ids}")  # Debugging line
            response = requests.post(url, headers=self.headers, json=proxy_ids)
        else:
            raise ValueError("Invalid input type for unlocking proxies.")
        
        return response.json()

    def get_proxy_ids(self, identifier: str) -> List[int]:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if the identifier is an IP address
        cursor.execute("SELECT id FROM proxies WHERE ip = ?", (identifier,))
        ids = cursor.fetchall()
        
        if not ids:
            # If not found by IP, check if it's a full address
            cursor.execute("SELECT id FROM proxies WHERE CONCAT(protocol, '://', username, ':', password, '@', ip, ':', port) = ?", (identifier,))
            ids = cursor.fetchall()
        
        conn.close()
        
        return [id[0] for id in ids]  # Return a list of IDs

    def health(self) -> dict:
        url = f"{self.base_url}/health"
        response = requests.get(url)
        return response.json()

    def get_all_available_proxies(self, auto_lock: bool = True) -> list:
        """Get all available proxies with option to auto-lock them"""
        url = f"{self.base_url}/available_proxies"
        params = {"auto_lock": auto_lock}
        response = requests.get(url, headers=self.headers, params=params)
        if response.status_code == 404:
            return []
        response.raise_for_status()
        return response.json()

    def refresh_proxies(self) -> dict:
        """Clear unused proxies and repopulate from proxies.txt"""
        url = f"{self.base_url}/refresh_proxies"
        response = requests.post(url, headers=self.headers)
        return response.json()
