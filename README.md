# FastAPI Proxy API

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.68%2B-green.svg)](https://fastapi.tiangolo.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A lightweight FastAPI application designed to manage proxies locally. This project was born from a personal need to share and manage proxies across multiple projects efficiently. Instead of manually configuring proxies for each application, this API serves as a centralized system to streamline proxy access and management.

## 🌟 **Key Features**

- **Centralized Management**: Single source of truth for all your proxy configurations
- **Dynamic Proxy Pool**: Add, remove, and modify proxies on the fly
- **Automatic Health Checks**: Background monitoring of proxy availability
- **Lock/Unlock System**: Prevent proxy conflicts between different applications
- **RESTful API**: Simple HTTP interface for proxy management
- **CLI Support**: Command-line interface for quick management tasks
- **Docker Ready**: Easy deployment with containerization
- **Secure Access**: API key authentication for protected endpoints

## 🚀 **Quick Start**

### Prerequisites
- Python 3.7+
- pip (Python package manager)
- Git
- Docker (optional)

### Basic Setup

1. **Clone the Repository**

```bash
git clone https://github.com/pudjojotaro/fastapi-proxy-api.git 
cd fastapi-proxy-api
```

2. **Create Virtual Environment** 
```bash
python -m venv venv

# Windows
.\venv\Scripts\activate

# Linux/MacOS
source venv/bin/activate
```

3. **Install Dependencies**
```bash
pip install -e .
```

4. **Configure Environment**
```bash
# Create .env file
echo "API_KEY=your-secure-api-key" > .env
```

5. **Prepare Proxy List**
Create a `proxies.txt` file in the root directory:
```
http://user:pass@192.168.1.100:8080
https://192.168.1.101:8081
```

6. **Initialize and Start**
```bash
# Start the API server
python main.py
# Or start in a new terminal window
start cmd /k "uvicorn main:app --host 0.0.0.0 --port 8000"
```

## 💻 **Usage Examples**

### Using the CLI

The package installs a `proxy-cli` command for easy management:

```bash
# Add a new proxy
proxy-cli add --protocol http --ip 192.168.1.100 --port 8080 --username user --password pass

# Test a proxy
proxy-cli test 1

# Get available proxies
proxy-cli get --count 2

# Unlock specific proxies
proxy-cli unlock "1,2,3"

# Start the server
proxy-cli start
```

### Using the API

1. **Add a Proxy**
```bash
curl -X POST "http://localhost:8000/add_proxy" \
     -H "X-API-Key: your-secure-api-key" \
     -H "Content-Type: application/json" \
     -d '{
           "protocol": "http",
           "ip": "192.168.1.100",
           "port": 8080,
           "username": "user",
           "password": "pass"
         }'
```

2. **Get Available Proxies**
```bash
curl -X GET "http://localhost:8000/get_proxies?count=2" \
     -H "X-API-Key: your-secure-api-key"
```

## 🐳 **Docker Deployment**

1. **Build the Image**
```bash
docker build -t fastapi-proxy-api .
```

2. **Run the Container**
```bash
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/proxies.txt:/app/proxies.txt \
  -v $(pwd)/proxies.db:/app/proxies.db \
  -e API_KEY=your-secure-api-key \
  fastapi-proxy-api
```

## 🔌 **Integration with Other Projects**

### Local Development Installation

You can install this package directly from your local copy for development:

```bash
# From your other project's directory
pip install -e path/to/fastapi-proxy-api

# Example
pip install -e ../fastapi-proxy-api
```

### Usage in Your Project

```python
from proxy_api import ProxyAPI

# Initialize the API client
proxy_api = ProxyAPI(
    api_key="your-secure-api-key",  # Optional: defaults to environment variable
    base_url="http://localhost:8000"  # Optional: defaults to this value
)

# Get a proxy
response = proxy_api.get_proxies(count=1)
proxy = response["proxies"][0]["proxy"]

# Use the proxy in your requests
import requests
proxies = {
    "http": proxy,
    "https": proxy
}
response = requests.get("https://example.com", proxies=proxies)
```

## 🎯 **API Documentation**

The main API handler (`handler.py`) provides the following endpoints and functionality:

### Core Endpoints

#### 1. Add Proxy (`POST /add_proxy`)
Adds a new proxy to the database.
```python
@app.post("/add_proxy")
def add_proxy(
    protocol: str,      # "http" or "https"
    ip: str,           # Proxy IP address
    port: int,         # Proxy port
    username: str = None,  # Optional auth
    password: str = None   # Optional auth
)
```

#### 2. Get Proxies (`GET /get_proxies`)
Retrieves and locks available proxies.
```python
@app.get("/get_proxies")
def get_proxies(
    count: int = 1,    # Number of proxies to retrieve
    format: str = "http://{username}:{password}@{ip}:{port}"  # Optional format
)
```

#### 3. Test Proxy (`GET /test_proxy/{proxy_id}`)
Tests if a specific proxy is working.
```python
@app.get("/test_proxy/{proxy_id}")
def test_proxy(proxy_id: int)
```

#### 4. Unlock Proxies (`POST /unlock_proxies`)
Unlocks specified proxies for reuse.
```python
@app.post("/unlock_proxies")
def unlock_proxies(proxies: List[int])
```

### Automatic Features

1. **Startup Actions**
   - Database initialization
   - Proxy conversion from text file
   - Unlocking all proxies

```python
@app.on_event("startup")
async def startup_event():
    init_db()
    convert_proxies()
    unlock_all_proxies()
```

2. **Shutdown Actions**
   - Automatic proxy unlocking

```python
@app.on_event("shutdown")
async def shutdown_event():
    unlock_all_proxies()
```

3. **Background Health Checks**
   - Hourly proxy testing
   - Automatic status updates

### Example Usage Scenarios

1. **Basic Proxy Retrieval**
```python
from proxy_api import ProxyAPI

api = ProxyAPI()

# Get a single proxy
proxy = api.get_proxies(count=1)
print(proxy["proxies"][0]["proxy"])
# Output: http://user:pass@192.168.1.100:8080

# Use the proxy
import requests
response = requests.get("https://example.com", proxies={
    "http": proxy["proxies"][0]["proxy"],
    "https": proxy["proxies"][0]["proxy"]
})
```

2. **Adding and Testing Proxies**
```python
# Add a new proxy
api.add_proxy(
    protocol="http",
    ip="192.168.1.100",
    port=8080,
    username="user",
    password="pass"
)

# Test a specific proxy
test_result = api.test_proxy(1)
print(test_result["message"])
# Output: "Proxy is working" or "Proxy failed"
```

3. **Managing Proxy Locks**
```python
# Get multiple proxies
proxies = api.get_proxies(count=3)
proxy_ids = [p["id"] for p in proxies["proxies"]]

# Use proxies...

# Unlock when done
api.unlock_proxies(proxy_ids)
```

### Error Handling

The API includes comprehensive error handling:

```python
try:
    proxies = api.get_proxies(count=5)
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 404:
        print("No available proxies")
    elif e.response.status_code == 403:
        print("Invalid API key")
    else:
        print(f"HTTP Error: {e}")
except requests.exceptions.RequestException as e:
    print(f"Connection error: {e}")
```

## 🔒 **Security Best Practices**

1. **API Key Protection**
   - Use a strong, unique API key
   - Store the key in environment variables
   - Rotate keys periodically

2. **Network Security**
   - Run behind a reverse proxy for SSL termination
   - Limit access to trusted IP addresses
   - Use HTTPS for production deployments

3. **Data Protection**
   - Set appropriate file permissions for `proxies.db`
   - Regularly backup your proxy database
   - Sanitize proxy credentials in logs

## 🛠️ **Advanced Configuration**

### Custom Health Checks
The API performs health checks every hour. To modify the interval, update the `check_proxies()` function in `handler.py`:

```python
await asyncio.sleep(3600)  # Modify this value (in seconds)
```

### Database Configuration
The SQLite database (`proxies.db`) is created automatically. To modify the schema:

```python:proxy_api/handler.py
startLine: 36
endLine: 52
```

## 📝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 **License**

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 **Support**

- Create an issue for bug reports or feature requests
- Star the repository if you find it useful
- Fork it to contribute improvements

## 🔗 **Resources**

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLite Documentation](https://www.sqlite.org/docs.html)
- [Docker Documentation](https://docs.docker.com/)
- [Python Virtual Environments](https://docs.python.org/3/tutorial/venv.html)

