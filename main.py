from fastapi import FastAPI
from proxy_api.handler import setup_routes

app = FastAPI()
setup_routes(app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)