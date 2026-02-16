# 🔧 Troubleshooting Guide

คู่มือแก้ไขปัญหาที่พบบ่อยใน IoT HTTP Workshop

---

## 📋 สารบัญปัญหา

1. [Wi-Fi Connection Issues](#1-wi-fi-connection-issues)
2. [HTTP Request Failures](#2-http-request-failures)
3. [JSON Validation Errors](#3-json-validation-errors)
4. [Server Issues](#4-server-issues)
5. [Network Configuration](#5-network-configuration)
6. [Arduino IDE Issues](#6-arduino-ide-issues)

---

## 1️⃣ Wi-Fi Connection Issues

### ปัญหา: WiFi connection failed

#### Symptoms (อาการ)
```
Connecting to WiFi........
❌ WiFi connection failed!
```

#### สาเหตุที่เป็นไปได้

| สาเหตุ | วิธีตรวจสอบ | วิธีแก้ไข |
|--------|-------------|-----------|
| **SSID ผิด** | ตรวจสอบชื่อ Wi-Fi | แก้ไขใน `WIFI_SSID` |
| **Password ผิด** | ตรวจสอบรหัสผ่าน | แก้ไขใน `WIFI_PASS` |
| **Wi-Fi 5GHz** | ESP32 รองรับแค่ 2.4GHz | เปลี่ยนเป็น 2.4GHz |
| **Signal อ่อน** | ตรวจสอบ RSSI | ย้าย ESP32 ใกล้ Router |
| **MAC Filter** | ตรวจสอบ Router settings | เพิ่ม MAC address ของ ESP32 |

#### วิธี Debug

```cpp
void connectWiFi() {
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  
  Serial.print("Connecting");
  int attempts = 0;
  
  while (WiFi.status() != WL_CONNECTED && attempts < 30) {
    delay(500);
    Serial.print(".");
    
    // แสดง WiFi status code
    Serial.print("(");
    Serial.print(WiFi.status());
    Serial.print(")");
    
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n✅ Connected!");
    Serial.print("SSID: ");
    Serial.println(WiFi.SSID());
    Serial.print("IP: ");
    Serial.println(WiFi.localIP());
    Serial.print("RSSI: ");
    Serial.print(WiFi.RSSI());
    Serial.println(" dBm");
  } else {
    Serial.println("\n❌ Failed!");
    Serial.print("Status Code: ");
    Serial.println(WiFi.status());
  }
}
```

#### WiFi Status Codes

| Code | ความหมาย |
|------|---------|
| 0 | WL_IDLE_STATUS |
| 1 | WL_NO_SSID_AVAIL (ไม่พบ SSID) |
| 3 | WL_CONNECTED |
| 4 | WL_CONNECT_FAILED (รหัสผ่านผิด) |
| 6 | WL_DISCONNECTED |

---

## 2️⃣ HTTP Request Failures

### ปัญหา: HTTP POST failed (Error code: -1)

#### Symptoms
```
📤 Sending data to server...
HTTP Response Code: -1
❌ HTTP POST failed!
Error: connection refused
```

#### สาเหตุและแนวทางแก้ไข

### สาเหตุที่ 1: Server IP ผิด

**ตรวจสอบ:**
```bash
# บน Raspberry Pi
hostname -I
```

**แก้ไข:**
```cpp
const char* SERVER_IP = "192.168.1.50";  // ใส่ IP ที่ถูกต้อง
```

### สาเหตุที่ 2: Server ไม่รัน

**ตรวจสอบ:**
```bash
# บน Raspberry Pi
curl http://localhost:8000
```

**แก้ไข:**
```bash
cd server
source .venv/bin/activate
uvicorn app:app --host 0.0.0.0 --port 8000
```

### สาเหตุที่ 3: Firewall Block

**ตรวจสอบ:**
```bash
sudo ufw status
sudo ss -lntp | grep 8000
```

**แก้ไข:**
```bash
sudo ufw allow 8000/tcp
sudo ufw reload
```

### สาเหตุที่ 4: ไม่ได้อยู่เน็ตเดียวกัน

**ตรวจสอบ:**
- ESP32 IP: `192.168.1.100`
- RPi IP: `192.168.1.50`
- ✅ **อยู่เน็ตเดียวกัน** (192.168.1.xxx)

**แก้ไข:**
- ต่อ ESP32 และ RPi เข้า Wi-Fi เดียวกัน

### สาเหตุที่ 5: DNS/Network Error

**ตรวจสอบ:**
```cpp
// Ping test
WiFiClient client;
if (client.connect(SERVER_IP, SERVER_PORT)) {
  Serial.println("✅ Can reach server!");
  client.stop();
} else {
  Serial.println("❌ Cannot reach server!");
}
```

---

## 3️⃣ JSON Validation Errors

### ปัญหา: HTTP Response Code: 422 (Unprocessable Entity)

#### Symptoms
```
HTTP Response Code: 422
⚠️  Server returned error
Response: {"detail":[{"loc":["body","temp"],"msg":"field required","type":"value_error.missing"}]}
```

#### สาเหตุ: JSON Format ไม่ตรง Schema

### ตัวอย่างที่ผิด

```cpp
// ❌ Field name ผิด
String payload = "{\"temperature\":28.5}";  // ต้องเป็น "temp"

// ❌ ขาด Field
String payload = "{\"device_id\":\"esp32-01\"}";  // ขาด temp, hum

// ❌ Data type ผิด
String payload = "{\"temp\":\"28.5\"}";  // ต้องเป็น Number ไม่ใช่ String
```

### ตัวอย่างที่ถูก

```cpp
// ✅ ถูกต้อง
String payload = "{";
payload += "\"device_id\":\"esp32-01\",";
payload += "\"temp\":" + String(28.5, 2) + ",";
payload += "\"hum\":" + String(65.3, 2) + ",";
payload += "\"source\":\"virtual\"";
payload += "}";
```

#### Schema ที่ Server ต้องการ

```json
{
  "device_id": "string (required)",
  "temp": "float (required)",
  "hum": "float (required)",
  "source": "string (optional)",
  "ts": "string (optional)"
}
```

#### วิธี Debug

```cpp
Serial.print("Payload: ");
Serial.println(payload);

// ตรวจสอบว่า JSON ถูกต้องไหมที่ jsonlint.com
```

---

## 4️⃣ Server Issues

### ปัญหา: HTTP Response Code: 500 (Internal Server Error)

#### Symptoms
```
HTTP Response Code: 500
⚠️  Server returned error
Response: {"detail":"Internal Server Error"}
```

#### วิธีแก้ไข

1. **ดู Server Logs**
```bash
# ใน terminal ที่รัน uvicorn จะมี error message
```

2. **Restart Server**
```bash
# กด CTRL+C แล้วรันใหม่
uvicorn app:app --host 0.0.0.0 --port 8000
```

3. **ตรวจสอบ Python Environment**
```bash
source .venv/bin/activate
pip list  # ดู installed packages
```

---

## 5️⃣ Network Configuration

### ตรวจสอบ Network Connectivity

#### Test 1: Ping RPi from Computer

```bash
ping 192.168.1.50
```

Expected:
```
64 bytes from 192.168.1.50: icmp_seq=1 ttl=64 time=1.23 ms
```

#### Test 2: Test API from Computer

```bash
curl http://192.168.1.50:8000
```

Expected:
```json
{"message":"RPi IoT Server is running",...}
```

#### Test 3: Post Data from Computer

```bash
curl -X POST http://192.168.1.50:8000/api/data \
  -H "Content-Type: application/json" \
  -d '{"device_id":"test","temp":25.0,"hum":60.0}'
```

Expected:
```json
{"ok":true,"message":"Data received successfully",...}
```

### หา IP Address

#### Raspberry Pi
```bash
hostname -I
# หรือ
ip addr show
```

#### ESP32 (ใน Serial Monitor)
```
WiFi connected!
IP Address: 192.168.1.100
```

#### Computer (Mac/Linux)
```bash
ifconfig
```

#### Computer (Windows)
```cmd
ipconfig
```

---

## 6️⃣ Arduino IDE Issues

### ปัญหา: Compilation Error

#### Error: WiFi.h: No such file or directory

**สาเหตุ:** ไม่ได้ติดตั้ง ESP32 board support

**แก้ไข:**
```
File → Preferences
Additional Boards Manager URLs:
https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json

Tools → Board → Boards Manager
ค้นหา "ESP32" → Install
```

#### Error: HTTPClient.h: No such file or directory

**สาเหตุ:** Board ไม่ได้เลือกเป็น ESP32

**แก้ไข:**
```
Tools → Board → ESP32 Arduino → ESP32 Dev Module
```

### ปัญหา: Upload Failed

#### Error: Failed to connect to ESP32

**สาเหตุ:** Port ผิดหรือ ESP32 ไม่เข้า boot mode

**แก้ไข:**
1. เลือก Port ใหม่ (Tools → Port)
2. กดปุ่ม BOOT ค้างไว้ขณะ Upload
3. ลอง Upload Speed ต่ำกว่า (115200)

---

## 🔍 Debugging Checklist

### ESP32 Side

- [ ] Wi-Fi SSID และ Password ถูกต้อง
- [ ] เชื่อมต่อ Wi-Fi สำเร็จ (เห็น IP Address)
- [ ] Server IP และ Port ถูกต้อง
- [ ] JSON Payload format ถูกต้อง
- [ ] Serial Monitor baud rate = 115200

### Server Side

- [ ] Python venv activated
- [ ] uvicorn รันอยู่
- [ ] Port 8000 เปิดอยู่
- [ ] Firewall ไม่ block
- [ ] `/docs` เปิดได้จาก browser

### Network Side

- [ ] ESP32 และ RPi อยู่ Wi-Fi เดียวกัน
- [ ] Ping ถึงกันได้
- [ ] ไม่มี VPN หรือ Proxy ขัดข้วง

---

## 🛠️ Debugging Tools

### 1. Serial Monitor (ESP32)

```cpp
Serial.println("Debug: WiFi connecting...");
Serial.print("Status: ");
Serial.println(WiFi.status());
Serial.print("IP: ");
Serial.println(WiFi.localIP());
```

### 2. FastAPI /docs (Server)

เปิด `http://<RPi_IP>:8000/docs`
- ทดสอบ POST /api/data
- ดูผล Response
- ตรวจสอบ Schema

### 3. curl (Command Line)

```bash
# Test GET
curl http://192.168.1.50:8000/api/latest

# Test POST
curl -X POST http://192.168.1.50:8000/api/data \
  -H "Content-Type: application/json" \
  -d '{"device_id":"test","temp":25.0,"hum":60.0}'
```

### 4. Python Test Script

```python
import requests

url = "http://192.168.1.50:8000/api/data"
data = {
    "device_id": "test",
    "temp": 25.0,
    "hum": 60.0
}

response = requests.post(url, json=data)
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")
```

---

## 📞 Getting Help

หากแก้ปัญหาไม่ได้ ให้:

1. **เก็บข้อมูล:**
   - Serial Monitor output (ESP32)
   - Server logs (Terminal ที่รัน uvicorn)
   - Network configuration (IP addresses)

2. **ตรวจสอบ Checklist:**
   - Wi-Fi connected?
   - Server running?
   - Same network?

3. **ถามคำถาม:**
   - GitHub Issues
   - Stack Overflow
   - Arduino Forum

---

## ✅ Quick Reference

### หา IP ของ Raspberry Pi
```bash
hostname -I
```

### Test Server
```bash
curl http://localhost:8000
```

### Test API
```bash
curl http://localhost:8000/api/latest
```

### Check Port
```bash
sudo ss -lntp | grep 8000
```

### Restart Server
```bash
# กด CTRL+C
uvicorn app:app --host 0.0.0.0 --port 8000
```

---

**หมายเหตุ:** ถ้ายังแก้ไม่ได้ ให้ลองรัน Workshop Checklist ใหม่ทั้งหมดตั้งแต่ต้น
