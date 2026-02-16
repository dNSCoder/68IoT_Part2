# 🌐 IoT HTTP Workshop: ESP32 + FastAPI

> **การเชื่อมต่อ IoT Device (ESP32) กับ Raspberry Pi Server ด้วย HTTP Protocol และ FastAPI**

[![Arduino](https://img.shields.io/badge/Arduino-00979D?style=flat&logo=arduino&logoColor=white)](https://www.arduino.cc/)
[![ESP32](https://img.shields.io/badge/ESP32-000000?style=flat&logo=espressif&logoColor=white)](https://www.espressif.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)

## 📚 Overview

Workshop นี้สอนการสร้างระบบ IoT แบบ **Client-Server** โดยใช้:
- **ESP32** เป็น IoT Device (Client) ส่งข้อมูล Sensor
- **Raspberry Pi** เป็น Server รับข้อมูลด้วย FastAPI
- **HTTP Protocol** เป็นช่องทางสื่อสาร
- **JSON** เป็นรูปแบบข้อมูล

## 🎯 Learning Objectives

หลังเรียนจบ Workshop นี้ คุณจะสามารถ:

1. ✅ เข้าใจบทบาท **Client-Server** ในระบบ IoT
2. ✅ ส่งข้อมูลจาก ESP32 ด้วย **HTTP POST + JSON**
3. ✅ สร้าง REST API ด้วย **FastAPI** บน Raspberry Pi
4. ✅ ทดสอบและ Debug ด้วย **FastAPI /docs** (Swagger UI)
5. ✅ ใช้ **Virtual Sensor** ก่อนเชื่อมต่อ Sensor จริง

## 📂 Repository Structure

```
iot-http-fastapi-workshop/
│
├── 📁 docs/                           # เอกสารประกอบการสอน
│   ├── 01-introduction.md             # แนะนำ HTTP, REST API, JSON
│   ├── 02-fastapi-basics.md           # FastAPI พื้นฐาน
│   ├── 03-esp32-httpclient.md         # ESP32 HTTPClient
│   └── 04-troubleshooting.md          # แก้ไขปัญหา
│
├── 📁 server/                         # FastAPI Server (Raspberry Pi)
│   ├── app.py                         # FastAPI application
│   ├── requirements.txt               # Python dependencies
│   └── README.md                      # วิธีติดตั้งและรัน
│
├── 📁 client/                         # Arduino/ESP32 Client
│   ├── iot_http_client/               # Arduino sketch folder
│   │   └── iot_http_client.ino       # Main sketch
│   ├── config.h.example               # ตัวอย่าง config file
│   └── README.md                      # วิธีใช้งาน Arduino sketch
│
├── 📁 examples/                       # ตัวอย่างเพิ่มเติม
│   ├── 01-simple-get/                 # HTTP GET request
│   ├── 02-virtual-sensor/             # Virtual Sensor (สำหรับทดสอบ)
│   └── 03-real-sensor/                # Real Sensor (BME280)
│
├── 📁 tools/                          # เครื่องมือช่วย
│   ├── test_api.py                    # Python script ทดสอบ API
│   └── find_rpi_ip.sh                 # หา IP ของ Raspberry Pi
│
└── README.md                          # ไฟล์นี้
```

## 🚀 Quick Start

### 1️⃣ Setup Server (Raspberry Pi)

```bash
# Clone repository
git clone <repository-url>
cd iot-http-fastapi-workshop/server

# สร้าง virtual environment
python3 -m venv .venv
source .venv/bin/activate

# ติดตั้ง dependencies
pip install -r requirements.txt

# รัน FastAPI server
uvicorn app:app --host 0.0.0.0 --port 8000
```

**ทดสอบ:** เปิดเบราว์เซอร์ไปที่ `http://<RPi_IP>:8000/docs`

### 2️⃣ Setup Client (ESP32)

1. เปิด Arduino IDE
2. ติดตั้ง ESP32 board support
3. เปิดไฟล์ `client/iot_http_client/iot_http_client.ino`
4. แก้ไข WiFi credentials และ Server IP
5. Upload ไปยัง ESP32
6. เปิด Serial Monitor (115200 baud)

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/data` | รับข้อมูลจาก IoT Device |
| `GET` | `/api/latest` | ดูข้อมูลล่าสุด |
| `GET` | `/docs` | Swagger UI (API Documentation) |

### Request Body Example (POST /api/data)

```json
{
  "device_id": "esp32-01",
  "temp": 28.50,
  "hum": 65.30,
  "source": "virtual",
  "ts": "2025-02-16T10:30:00Z"
}
```

### Response Example

```json
{
  "ok": true,
  "latest": {
    "device_id": "esp32-01",
    "temp": 28.50,
    "hum": 65.30,
    "source": "virtual",
    "ts": "2025-02-16T10:30:00Z"
  }
}
```

## 🔧 System Requirements

### Server (Raspberry Pi)
- Raspberry Pi 3/4/5
- Raspbian OS (64-bit recommended)
- Python 3.8+
- Network connection

### Client (ESP32)
- ESP32 Development Board
- Arduino IDE 2.x
- ESP32 Board Support (arduino-esp32)
- Libraries: `WiFi.h`, `HTTPClient.h`

## 📖 Workshop Steps

### **Step A: เตรียม Server (FastAPI)**

1. สร้างโปรเจกต์และ virtual environment
2. เขียน `app.py` ตาม template
3. รัน server ด้วย uvicorn
4. ทดสอบผ่าน `/docs` (Swagger UI)

### **Step B: เตรียม Client (ESP32)**

1. เชื่อมต่อ WiFi
2. สร้าง Virtual Sensor (สุ่มค่า temp/hum)
3. ส่ง HTTP POST ไปยัง Server ทุก 3 วินาที
4. ตรวจสอบ Response ใน Serial Monitor

### **Step C: ทดสอบและ Debug**

1. ตรวจสอบ IP ของ Raspberry Pi
2. ตรวจสอบ WiFi connection
3. ดู HTTP status code
4. แก้ไข JSON format หากมีปัญหา

## 🐛 Troubleshooting

| ปัญหา | สาเหตุที่เป็นไปได้ | แนวทางแก้ไข |
|-------|-------------------|-------------|
| **422 Unprocessable Entity** | JSON format ไม่ตรงกับ schema | ตรวจสอบ field names และ data types |
| **Connection Failed** | WiFi / IP ไม่ถูกต้อง | ตรวจสอบ SSID, Password, IP |
| **Timeout** | Server ไม่รัน หรือ firewall block | ตรวจสอบ `uvicorn` รันอยู่ไหม |
| **-1 Error Code** | DNS / Network error | ตรวจสอบ WiFi connection |

## 📚 Additional Resources

### FastAPI
- [FastAPI Official Docs](https://fastapi.tiangolo.com/)
- [GeeksforGeeks: FastAPI Tutorial](https://www.geeksforgeeks.org/python/fastapi-tutorial/)
- [Pydantic Documentation](https://docs.pydantic.dev/)

### ESP32 HTTP Client
- [Random Nerd Tutorials: ESP32 HTTP](https://randomnerdtutorials.com/esp32-http-get-post-arduino/)
- [ESP32 Arduino Core](https://github.com/espressif/arduino-esp32)
- [HTTPClient Library Reference](https://github.com/espressif/arduino-esp32/tree/master/libraries/HTTPClient)

### REST API Concepts
- [RESTful API Design](https://restfulapi.net/)
- [HTTP Status Codes](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status)
- [JSON.org](https://www.json.org/)

## 🎓 Learning Path

```
1️⃣ HTTP Basics          → เข้าใจ Client-Server, GET/POST
2️⃣ JSON Format          → รู้จักโครงสร้างข้อมูล JSON
3️⃣ FastAPI Setup        → ติดตั้งและรัน Server
4️⃣ Virtual Sensor       → ทดสอบส่งข้อมูลจำลอง
5️⃣ Real Sensor (BME280) → เชื่อมต่อ Sensor จริง
6️⃣ Database (Optional)  → เก็บข้อมูลใน SQLite/MongoDB
```

## 🤝 Contributing

เรายินดีรับ Pull Request! หากพบปัญหาหรือต้องการเพิ่มเนื้อหา:

1. Fork repository นี้
2. สร้าง feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit การเปลี่ยนแปลง (`git commit -m 'Add some AmazingFeature'`)
4. Push ไปยัง branch (`git push origin feature/AmazingFeature`)
5. เปิด Pull Request

## 📝 License

MIT License - ใช้งานได้ฟรีเพื่อการศึกษา

## 📧 Contact

หากมีคำถาม สามารถติดต่อได้ที่:
- GitHub Issues: [Create Issue](../../issues)
- Email: [your-email@example.com]

---

**Made with ❤️ for IoT Education**
