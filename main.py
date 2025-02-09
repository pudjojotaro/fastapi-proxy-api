from fastapi import FastAPI
from proxy_api.handler import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)