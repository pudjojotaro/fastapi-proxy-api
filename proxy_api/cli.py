import typer
from api import ProxyAPI
from typing import Optional
import os

app = typer.Typer()
api = ProxyAPI()

@app.command()
def add(protocol: str, ip: str, port: int, username: Optional[str] = None, password: Optional[str] = None):
    """Add a new proxy"""
    result = api.add_proxy(protocol, ip, port, username, password)
    typer.echo(result)

@app.command()
def test(proxy_id: int):
    """Test a specific proxy"""
    result = api.test_proxy(proxy_id)
    typer.echo(result)

@app.command()
def get(count: int = 1):
    """Get available proxies"""
    result = api.get_proxies(count)
    typer.echo(result)

@app.command()
def unlock(proxy_ids: str):
    """Unlock proxies (comma-separated IDs)"""
    ids = [int(id.strip()) for id in proxy_ids.split(",")]
    result = api.unlock_proxies(ids)
    typer.echo(result)

@app.command()
def start():
    """Start the proxy server"""
    os.system("uvicorn handler:app --host 0.0.0.0 --port 8000")

@app.command()
def refresh():
    """Clear unused proxies and repopulate from proxies.txt"""
    result = api.refresh_proxies()
    typer.echo(result)

if __name__ == "__main__":
    app() 