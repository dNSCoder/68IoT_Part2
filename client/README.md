# 📱 ESP32 HTTP Client Setup

Arduino sketch สำหรับส่งข้อมูลจาก ESP32 ไปยัง FastAPI Server

## 📋 Requirements

### Hardware
- ESP32 Development Board
- USB Cable (สำหรับ upload และ power)
- Computer สำหรับ programming

### Software
- [Arduino IDE 2.x](https://www.arduino.cc/en/software) หรือสูงกว่า
- ESP32 Board Support Package

## 🔧 Arduino IDE Setup

### 1. ติดตั้ง ESP32 Board Support

#### วิธีที่ 1: ผ่าน Boards Manager (แนะนำ)

1. เปิด Arduino IDE
2. ไปที่ **File → Preferences**
3. ใส่ URL นี้ใน "Additional Boards Manager URLs":
   ```
   https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
   ```
4. คลิก **OK**
5. ไปที่ **Tools → Board → Boards Manager**
6. ค้นหา "ESP32"
7. ติดตั้ง **"ESP32 by Espressif Systems"** (เวอร์ชันล่าสุด)

#### วิธีที่ 2: Manual Installation (สำหรับ Advanced Users)

```bash
cd ~/Arduino/hardware
mkdir -p espressif
cd espressif
git clone https://github.com/espressif/arduino-esp32.git esp32
cd esp32
git submodule update --init --recursive
cd tools
python3 get.py
```

### 2. เลือก Board

1. เชื่อมต่อ ESP32 กับ Computer
2. ไปที่ **Tools → Board → ESP32 Arduino**
3. เลือก board ของคุณ (เช่น **ESP32 Dev Module**)
4. เลือก **Port** ที่ถูกต้อง (**Tools → Port**)

### 3. ตรวจสอบ Libraries

ESP32 มี libraries ในตัวแล้ว ไม่ต้องติดตั้งเพิ่ม:
- ✅ `WiFi.h` - สำหรับเชื่อมต่อ Wi-Fi
- ✅ `HTTPClient.h` - สำหรับส่ง HTTP requests

## 📝 Configuration

### 1. คัดลอก Config Template

```bash
cp config.h.example config.h
```

### 2. แก้ไข config.h

```cpp
// Wi-Fi Settings
#define WIFI_SSID "YourWiFiName"
#define WIFI_PASS "YourWiFiPassword"

// Server Settings (IP ของ Raspberry Pi)
#define SERVER_IP   "192.168.1.50"
#define SERVER_PORT 8000

// Device Settings
#define DEVICE_ID "esp32-01"  // เปลี่ยนให้ไม่ซ้ำกัน
```

### 3. หา IP ของ Raspberry Pi

บน Raspberry Pi รันคำสั่ง:
```bash
hostname -I
```

Output ตัวอย่าง:
```
192.168.1.50
```

นำ IP นี้ไปใส่ใน `SERVER_IP`

## ⬆️ Uploading to ESP32

### 1. เปิด Sketch

```
File → Open → iot_http_client/iot_http_client.ino
```

### 2. ตรวจสอบการตั้งค่า

- **Board**: ESP32 Dev Module (หรือรุ่นที่ตรง)
- **Upload Speed**: 115200 (หรือ 921600 ถ้ารองรับ)
- **CPU Frequency**: 240MHz
- **Flash Size**: 4MB (หรือตามที่มี)
- **Port**: เลือก port ที่เชื่อมต่อ

### 3. Compile และ Upload

1. คลิก **Verify** (✓) เพื่อ compile
2. คลิก **Upload** (→) เพื่อ upload
3. รอจนกว่าจะเห็น "Done uploading"

## 🔍 Testing & Debugging

### 1. เปิด Serial Monitor

- คลิก **Tools → Serial Monitor**
- ตั้ง baud rate เป็น **115200**

### 2. ตรวจสอบ Output

```
================================================
  IoT HTTP Client - ESP32
  Virtual Sensor → FastAPI Server
================================================

Connecting to WiFi.....
✅ WiFi connected!
IP Address: 192.168.1.100
Signal Strength (RSSI): -45 dBm

⚙️  Configuration:
Device ID: esp32-01
Server: http://192.168.1.50:8000
Send Interval: 3 seconds

🚀 ESP32 HTTP IoT Client is ready!
================================================

📊 Sensor Reading:
  Temperature: 28.45 °C
  Humidity: 65.23 %

📤 Sending data to server...
URL: http://192.168.1.50:8000/api/data
Payload: {"device_id":"esp32-01","temp":28.45,"hum":65.23,"source":"virtual"}
HTTP Response Code: 200
✅ Data sent successfully!
Response: {"ok":true,"message":"Data received successfully","latest":{...}}

✨ Cycle completed successfully!
================================================
```

## 🐛 Common Issues

### ปัญหา: WiFi connection failed

**สาเหตุ:**
- SSID หรือ Password ผิด
- Wi-Fi อยู่นอกระยะ
- Wi-Fi ใช้ 5GHz (ESP32 รองรับแค่ 2.4GHz)

**แนวทางแก้ไข:**
```cpp
// เพิ่ม debug info
Serial.println(WiFi.status());  // ดู status code
Serial.println(WiFi.SSID());    // ดู SSID ที่เชื่อมต่อ
```

### ปัญหา: HTTP POST failed (Error code: -1)

**สาเหตุ:**
- Server IP ผิด
- Server ไม่รัน
- ESP32 และ Server ไม่ได้อยู่เน็ตเดียวกัน
- Firewall block

**แนวทางแก้ไข:**
1. ตรวจสอบ Server รันอยู่:
   ```bash
   curl http://localhost:8000
   ```
2. Ping จาก ESP32 ไป RPi (ทดสอบ network)
3. ตรวจสอบ Firewall ของ RPi

### ปัญหา: HTTP Response Code: 422

**สาเหตุ:**
- JSON format ไม่ตรงกับ schema ของ Server
- ข้อมูลผิด data type

**แนวทางแก้ไข:**
- ตรวจสอบ JSON payload ที่ส่ง
- ดูใน Serial Monitor ว่า payload ถูกต้องไหม
- เปรียบเทียบกับ schema ใน server

### ปัญหา: Compilation Error

**สาเหตุ:**
- Library ไม่ครบ
- Board support ไม่ถูกต้อง

**แนวทางแก้ไข:**
```bash
# ตรวจสอบ ESP32 core version
Arduino IDE → Tools → Board → Boards Manager → ESP32

# อัปเดตเป็นเวอร์ชันล่าสุด
```

## 📊 Expected Serial Monitor Output

### Success Case ✅

```
WiFi connected!
IP Address: 192.168.1.100

📊 Sensor Reading:
  Temperature: 28.45 °C
  Humidity: 65.23 %

📤 Sending data to server...
HTTP Response Code: 200
✅ Data sent successfully!
```

### Failure Cases ❌

#### Case 1: Network Error
```
❌ HTTP POST failed!
Error: connection refused
```

#### Case 2: Server Error
```
HTTP Response Code: 500
⚠️  Server returned error
Response: {"detail":"Internal Server Error"}
```

#### Case 3: Validation Error
```
HTTP Response Code: 422
⚠️  Server returned error
Response: {"detail":[{"loc":["body","temp"],"msg":"field required","type":"value_error.missing"}]}
```

## 🔗 Pin Configuration

### Default Pins สำหรับ Real Sensors (ใช้ในคลาสถัดไป)

```
BME280 (I2C):
- SDA → GPIO 21
- SCL → GPIO 22
- VCC → 3.3V
- GND → GND

DHT22:
- DATA → GPIO 4
- VCC  → 3.3V
- GND  → GND
```

## 📚 Code Structure

```
iot_http_client.ino
├── Configuration Section
│   ├── WiFi credentials
│   ├── Server settings
│   └── Device ID
│
├── Functions
│   ├── connectWiFi()          - เชื่อมต่อ Wi-Fi
│   ├── virtualTemp()          - สร้างค่า temp แบบสุ่ม
│   ├── virtualHum()           - สร้างค่า hum แบบสุ่ม
│   ├── createJsonPayload()    - สร้าง JSON string
│   └── sendDataToServer()     - ส่ง HTTP POST
│
├── setup()
│   ├── เริ่ม Serial
│   ├── เชื่อมต่อ WiFi
│   └── แสดงการตั้งค่า
│
└── loop()
    ├── เช็ค WiFi connection
    ├── อ่านค่า sensor (virtual)
    └── ส่งข้อมูลทุก 3 วินาที
```

## 🎓 Next Steps

1. ✅ ทำให้ Virtual Sensor ทำงานได้
2. ⏭️ เปลี่ยนเป็น Real Sensor (BME280 หรือ DHT22)
3. ⏭️ เพิ่ม Error Handling และ Retry Logic
4. ⏭️ เพิ่ม Sleep Mode เพื่อประหยัดไฟ
5. ⏭️ เก็บข้อมูลใน Database (Server side)

## 🔗 Related Files

- `iot_http_client.ino` - Main Arduino sketch
- `config.h.example` - Configuration template
- `../server/` - FastAPI server code
- `../docs/` - Documentation
- `../examples/` - Additional examples
