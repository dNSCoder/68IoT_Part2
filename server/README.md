# 🖥️ FastAPI Server Setup

Server สำหรับรับข้อมูลจาก IoT Devices ด้วย FastAPI

## 📋 Requirements

- Python 3.8 หรือสูงกว่า
- pip (Python package installer)
- Raspberry Pi หรือ Linux computer
- Network connection

## 🚀 Installation

### 1. สร้าง Virtual Environment

```bash
# ติดตั้ง python3-venv (ถ้ายังไม่มี)
sudo apt update
sudo apt install -y python3-venv

# สร้าง virtual environment
cd server
python3 -m venv .venv

# เปิดใช้งาน virtual environment
source .venv/bin/activate  # Linux/Mac
# หรือ
.venv\Scripts\activate  # Windows
```

### 2. ติดตั้ง Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. ตรวจสอบการติดตั้ง

```bash
python -c "import fastapi; print(f'FastAPI version: {fastapi.__version__}')"
python -c "import uvicorn; print(f'Uvicorn version: {uvicorn.__version__}')"
```

## ▶️ Running the Server

### วิธีที่ 1: รันโดยตรง (Development Mode)

```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

**Parameters:**
- `--host 0.0.0.0`: ฟังจากทุก network interface (ให้ device อื่นเข้าถึงได้)
- `--port 8000`: ใช้ port 8000
- `--reload`: Auto-reload เมื่อมีการแก้ไขโค้ด (ใช้ตอน development)

### วิธีที่ 2: รันแบบ Production

```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 2
```

**Parameters:**
- `--workers 2`: รัน 2 worker processes (เพิ่ม performance)

## 🔍 Testing the Server

### 1. ตรวจสอบว่า Server รันอยู่

```bash
# ใน terminal อื่น
curl http://localhost:8000
```

**Expected Output:**
```json
{
  "message": "RPi IoT Server is running",
  "version": "1.0.0",
  "endpoints": {...}
}
```

### 2. ทดสอบผ่าน Swagger UI

เปิดเบราว์เซอร์:
```
http://<RPi_IP>:8000/docs
```

### 3. ทดสอบ POST ข้อมูล

```bash
curl -X POST http://localhost:8000/api/data \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "test-device",
    "temp": 25.5,
    "hum": 60.0,
    "source": "manual"
  }'
```

**Expected Output:**
```json
{
  "ok": true,
  "message": "Data received successfully",
  "latest": {...}
}
```

### 4. ดึงข้อมูลล่าสุด

```bash
curl http://localhost:8000/api/latest
```

## 🌐 Finding Raspberry Pi IP Address

```bash
hostname -I
```

หรือ

```bash
ip addr show | grep inet
```

## 🔒 Firewall Configuration

หาก Raspberry Pi มี firewall:

```bash
# UFW
sudo ufw allow 8000/tcp

# หรือ firewalld
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload
```

## 📊 Monitoring Logs

Server จะแสดง log ใน terminal:

```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

เมื่อรับข้อมูล:
```
[RECV] {'device_id': 'esp32-01', 'temp': 28.5, 'hum': 65.3, 'source': 'virtual', 'ts': '2025-02-16T10:30:00Z'}
```

## 🛑 Stopping the Server

กด `CTRL+C` ใน terminal

## 🔧 Configuration Options

### เปลี่ยน Port

```bash
uvicorn app:app --host 0.0.0.0 --port 5000
```

### เปิดใช้ CORS (สำหรับ Web Client)

แก้ไขไฟล์ `app.py`:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 🐛 Troubleshooting

### ปัญหา: Port already in use

```bash
# หา process ที่ใช้ port 8000
sudo lsof -i :8000

# หรือ
sudo ss -lntp | grep 8000

# ปิด process (ใช้ PID ที่ได้)
kill <PID>
```

### ปัญหา: Permission denied

```bash
# ใช้ port > 1024 หรือ
sudo uvicorn app:app --host 0.0.0.0 --port 80
```

### ปัญหา: Module not found

```bash
# ตรวจสอบว่าอยู่ใน virtual environment
which python

# ติดตั้ง dependencies ใหม่
pip install -r requirements.txt
```

## 📚 API Documentation

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | ข้อมูลพื้นฐานของ API |
| `POST` | `/api/data` | รับข้อมูลจาก IoT Device |
| `GET` | `/api/latest` | ดูข้อมูลล่าสุด |
| `GET` | `/health` | Health check |
| `GET` | `/docs` | Swagger UI |
| `GET` | `/redoc` | ReDoc UI |

### Request Body Schema (POST /api/data)

```json
{
  "device_id": "string (required)",
  "temp": "float (required)",
  "hum": "float (required)",
  "source": "string (optional, default: 'unknown')",
  "ts": "string (optional, ISO format)"
}
```

## 📈 Production Deployment

### ใช้ systemd service

สร้างไฟล์ `/etc/systemd/system/iot-server.service`:

```ini
[Unit]
Description=IoT FastAPI Server
After=network.target

[Service]
User=pi
WorkingDirectory=/home/pi/iot-http-fastapi-workshop/server
Environment="PATH=/home/pi/iot-http-fastapi-workshop/server/.venv/bin"
ExecStart=/home/pi/iot-http-fastapi-workshop/server/.venv/bin/uvicorn app:app --host 0.0.0.0 --port 8000 --workers 2

[Install]
WantedBy=multi-user.target
```

เปิดใช้งาน:
```bash
sudo systemctl daemon-reload
sudo systemctl enable iot-server
sudo systemctl start iot-server
sudo systemctl status iot-server
```

## 🔗 Related Files

- `app.py` - Main FastAPI application
- `requirements.txt` - Python dependencies
- `../client/` - ESP32 client code
- `../docs/` - Documentation
