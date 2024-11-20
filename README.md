# FastAPI Proxy API

A lightweight FastAPI application to manage proxies locally. Users can add, test, retrieve, lock, and unlock proxies with ease.

## 📦 **Features**

- **Add Proxies**: Manually add proxies with detailed information.
- **Test Proxies**: Validate proxy functionality.
- **Retrieve Proxies**: Get multiple available proxies in a specified format.
- **Lock/Unlock Proxies**: Manage proxy usage to prevent conflicts.
- **Background Health Checks**: Periodically verify proxy health.
- **Secure Access**: Optional API key protection.
- **Local Deployment**: Easily run the API on your local machine.

## 🔧 **Setup Instructions**

### 1. **Clone the Repository**

```bash
git clone https://github.com/pudjojotaro/fastapi-proxy-api.git
cd fastapi-proxy-api
```

### 2. **Set Up Virtual Environment**

It's recommended to use a virtual environment to manage dependencies.

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
.\venv\Scripts\activate
```

### 3. **Install Dependencies**

```bash
pip install -r requirements.txt
```

### 4. **Prepare `proxies.txt`**

Add your proxies to the `proxies.txt` file in the following formats:

- **With Authentication:**
  ```
  http://username:password@ip:port
  https://username:password@ip:port
  ```

- **Without Authentication:**
  ```
  http://ip:port
  https://ip:port
  ```

**Example:**
```
http://user1:pass1@192.168.1.100:8080
https://192.168.1.101:8081
http://user2:pass2@192.168.1.102:8082
```

### 5. **Convert and Load Proxies**

Run the `proxy_converter.py` script to parse the `proxies.txt` file and populate the `proxies.db` database.

```bash
python proxy_converter.py
```

**Output Example:**
```
2023-09-24 12:34:56,789 - INFO - Inserted proxy: http://user1:pass1@192.168.1.100:8080
2023-09-24 12:34:56,790 - INFO - Inserted proxy: https://@192.168.1.101:8081
2023-09-24 12:34:56,791 - INFO - Inserted proxy: http://user2:pass2@192.168.1.102:8082
2023-09-24 12:34:56,792 - INFO - Proxy conversion completed.
```

### 6. **Set Up Environment Variables**

Create a `.env` file to store your API key for enhanced security.

```bash
touch .env
```

**Add the following line to `.env`:**
```
API_KEY=your-secure-api-key
```

*Replace `your-secure-api-key` with a strong, unique key.*

### 7. **Run the FastAPI Server**

Start the FastAPI application using Uvicorn.

```bash
uvicorn handler:app --host 0.0.0.0 --port 8000
```

### 8. **Access the API Documentation**

Navigate to [http://localhost:8000/docs](http://localhost:8000/docs) in your browser to view the interactive Swagger UI.

## 🚀 **API Endpoints**

### 1. **Add a Proxy**

- **Endpoint:** `POST /add_proxy`
- **Headers:**
  - `X-API-Key: your-secure-api-key`
- **Body Parameters:**
  - `protocol` (str): `http` or `https`
  - `ip` (str): Proxy IP address
  - `port` (int): Proxy port
  - `username` (str, optional): Proxy username
  - `password` (str, optional): Proxy password

**Example Request:**

```bash
curl -X POST "http://localhost:8000/add_proxy" \
     -H "Content-Type: application/json" \
     -H "X-API-Key: your-secure-api-key" \
     -d '{
           "protocol": "http",
           "ip": "192.168.1.103",
           "port": 8083,
           "username": "user3",
           "password": "pass3"
         }'
```

**Response:**
```json
{
  "message": "Proxy added successfully"
}
```

### 2. **Test a Proxy by ID**

- **Endpoint:** `GET /test_proxy/{proxy_id}`
- **Headers:**
  - `X-API-Key: your-secure-api-key`
- **Path Parameters:**
  - `proxy_id` (int): ID of the proxy to test

**Example Request:**

```bash
curl -X GET "http://localhost:8000/test_proxy/1" \
     -H "X-API-Key: your-secure-api-key"
```

**Response:**
```json
{
  "message": "Proxy is working"
}
```

### 3. **Retrieve Multiple Proxies**

- **Endpoint:** `GET /get_proxies`
- **Headers:**
  - `X-API-Key: your-secure-api-key`
- **Query Parameters:**
  - `count` (int, optional): Number of proxies to retrieve (default: 1)
  - `format` (str, optional): Format of the proxy URL (default: `"http://{username}:{password}@{ip}:{port}"`)

**Example Request:**

```bash
curl -X GET "http://localhost:8000/get_proxies?count=2" \
     -H "X-API-Key: your-secure-api-key"
```

**Response:**
```json
{
  "proxies": [
    {
      "id": 1,
      "proxy": "http://user1:pass1@192.168.1.100:8080"
    },
    {
      "id": 2,
      "proxy": "https://192.168.1.101:8081"
    }
  ]
}
```

### 4. **Unlock Proxies by IDs**

- **Endpoint:** `POST /unlock_proxies`
- **Headers:**
  - `X-API-Key: your-secure-api-key`
- **Body Parameters:**
  - `proxies` (List[int]): List of proxy IDs to unlock

**Example Request:**

```bash
curl -X POST "http://localhost:8000/unlock_proxies" \
     -H "Content-Type: application/json" \
     -H "X-API-Key: your-secure-api-key" \
     -d '{
           "proxies": [1, 2]
         }'
```

**Response:**
```json
{
  "message": "Proxies unlocked successfully"
}
```

### 5. **Health Check**

- **Endpoint:** `GET /health`
- **Description:** Check if the API is running.

**Example Request:**

```bash
curl -X GET "http://localhost:8000/health"
```

**Response:**
```json
{
  "status": "healthy"
}
```

## 🐳 **Docker Usage**

Containerizing your application ensures consistency across different user environments and simplifies the setup process.

### 1. **Build the Docker Image**

```bash
docker build -t fastapi-proxy-api .
```

### 2. **Run the Docker Container**

```bash
docker run -d -p 8000:8000 -v $(pwd)/proxies.db:/app/proxies.db fastapi-proxy-api
```

**Advantages:**
- **Consistency**: Ensures the application runs the same way on all user machines.
- **Ease of Setup**: Users only need Docker installed to run the API.

## 📄 **`.gitignore`**

To prevent sensitive files and unnecessary directories from being pushed to GitHub, use the following `.gitignore`:

```gitignore
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# Virtual environments
venv/
env/
.venv/
.env

# Database files
proxies.db

# Logs
*.log

# macOS specific
.DS_Store
```

## 🛡️ **Security Considerations**

### 1. **API Key Protection**

To prevent unauthorized access to your local API, use an API key.

- **Setting the API Key:**
  - **Option 1:** Set it as an environment variable before running the server.
    ```bash
    export API_KEY="your-secure-api-key"
    uvicorn handler:app --host 0.0.0.0 --port 8000
    ```
  - **Option 2:** Include it in the `.env` file.

- **Usage:**
  - All API requests must include the header `X-API-Key` with the correct key.

### 2. **HTTPS Setup (Recommended)**

For local deployments, securing the API with HTTPS enhances security, especially if exposed beyond `localhost`.

- **Use a Reverse Proxy with Nginx:**

  1. **Install Nginx:**
     ```bash
     sudo apt update
     sudo apt install nginx -y
     ```

  2. **Configure Nginx:**
     ```bash
     sudo nano /etc/nginx/sites-available/proxy-api
     ```
     **Example Configuration:**
     ```nginx
     server {
         listen 80;
         server_name localhost;

         location / {
             proxy_pass http://127.0.0.1:8000;
             proxy_set_header Host $host;
             proxy_set_header X-Real-IP $remote_addr;
             proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
             proxy_set_header X-Forwarded-Proto $scheme;
         }
     }
     ```

  3. **Enable the Configuration and Restart Nginx:**
     ```bash
     sudo ln -s /etc/nginx/sites-available/proxy-api /etc/nginx/sites-enabled/
     sudo nginx -t  # Test configuration
     sudo systemctl restart nginx
     ```

  4. **Set Up SSL (Optional for Local):**
     For development purposes, you can use self-signed certificates or tools like [mkcert](https://github.com/FiloSottile/mkcert).

### 3. **Database Security**

- **File Permissions:**
  Ensure that `proxies.db` has appropriate file permissions to prevent unauthorized access.
  ```bash
  chmod 600 proxies.db
  ```

- **Environment Variables:**
  Store sensitive information, like API keys, in environment variables or secure configuration files, not in the codebase.



## 🔗 **Helpful Resources**

- [GitHub CLI Documentation](https://cli.github.com/manual/)
- [GitHub Docs: Creating a Repository](https://docs.github.com/en/get-started/quickstart/create-a-repo)
- [Git Basics](https://git-scm.com/doc)
- [GitHub Docs: Managing Remote Repositories](https://docs.github.com/en/github/using-git/managing-remote-repositories)
- [Docker Installation Guide](https://docs.docker.com/get-docker/)

