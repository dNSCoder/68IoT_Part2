/*
 * IoT HTTP Client for ESP32
 * ===========================
 * ส่งข้อมูล Sensor (Virtual) ไปยัง FastAPI Server ด้วย HTTP POST
 * 
 * Hardware: ESP32 Development Board
 * Libraries: WiFi.h, HTTPClient.h (Built-in with ESP32 Arduino Core)
 * 
 * Author: Workshop Materials
 * Date: February 2025
 */

#include <WiFi.h>            // Wi-Fi library สำหรับ ESP32
#include <HTTPClient.h>      // HTTP client library

// ==================== Configuration ====================

// Wi-Fi Credentials (แก้ไขตามของคุณ)
const char* WIFI_SSID = "YOUR_WIFI_SSID";        // ชื่อ Wi-Fi
const char* WIFI_PASS = "YOUR_WIFI_PASSWORD";    // รหัสผ่าน Wi-Fi

// Server Configuration (แก้ไข IP ให้ตรงกับ Raspberry Pi)
const char* SERVER_IP   = "192.168.1.50";        // IP Address ของ RPi
const int   SERVER_PORT = 8000;                  // Port ของ FastAPI Server

// Device Configuration
String deviceId = "esp32-01";                    // Device ID (ตั้งชื่อไม่ซ้ำกัน)

// Timing Configuration
unsigned long lastSendMs = 0;                    // เวลาส่งข้อมูลล่าสุด (milliseconds)
const unsigned long SEND_INTERVAL_MS = 3000;     // ส่งข้อมูลทุก 3 วินาที


// ==================== Functions ====================

/**
 * เชื่อมต่อ Wi-Fi
 */
void connectWiFi() {
  WiFi.mode(WIFI_STA);                           // ตั้งโหมด Station (Client)
  WiFi.begin(WIFI_SSID, WIFI_PASS);              // เริ่มเชื่อมต่อ

  Serial.print("Connecting to WiFi");
  int attempts = 0;
  
  while (WiFi.status() != WL_CONNECTED && attempts < 30) {
    delay(500);
    Serial.print(".");
    attempts++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println();
    Serial.println("✅ WiFi connected!");
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());
    Serial.print("Signal Strength (RSSI): ");
    Serial.print(WiFi.RSSI());
    Serial.println(" dBm");
  } else {
    Serial.println();
    Serial.println("❌ WiFi connection failed!");
  }
}

/**
 * สร้างค่า Temperature แบบสุ่ม (Virtual Sensor)
 * @return float - อุณหภูมิ 25.00 - 33.00 °C
 */
float virtualTemp() {
  return 25.0 + (random(0, 800) / 100.0);
}

/**
 * สร้างค่า Humidity แบบสุ่ม (Virtual Sensor)
 * @return float - ความชื้น 40.00 - 80.00 %
 */
float virtualHum() {
  return 40.0 + (random(0, 4000) / 100.0);
}

/**
 * สร้าง JSON Payload
 * @param deviceId - Device ID
 * @param temp - Temperature value
 * @param hum - Humidity value
 * @return String - JSON string
 */
String createJsonPayload(String deviceId, float temp, float hum) {
  String payload = "{";
  payload += "\"device_id\":\"" + deviceId + "\",";
  payload += "\"temp\":" + String(temp, 2) + ",";
  payload += "\"hum\":" + String(hum, 2) + ",";
  payload += "\"source\":\"virtual\"";
  payload += "}";
  return payload;
}

/**
 * ส่งข้อมูลไปยัง Server ด้วย HTTP POST
 * @param temp - Temperature value
 * @param hum - Humidity value
 * @return bool - true ถ้าส่งสำเร็จ
 */
bool sendDataToServer(float temp, float hum) {
  // สร้าง URL
  String url = "http://" + String(SERVER_IP) + ":" + String(SERVER_PORT) + "/api/data";
  
  // สร้าง JSON Payload
  String payload = createJsonPayload(deviceId, temp, hum);

  // แสดงข้อมูลที่จะส่ง
  Serial.println("\n📤 Sending data to server...");
  Serial.print("URL: ");
  Serial.println(url);
  Serial.print("Payload: ");
  Serial.println(payload);

  // สร้าง HTTP Client
  HTTPClient http;
  http.begin(url);                                      // ตั้ง URL
  http.addHeader("Content-Type", "application/json");  // ตั้ง Header
  http.setTimeout(5000);                               // Timeout 5 วินาที

  // ส่ง HTTP POST Request
  int httpCode = http.POST(payload);

  // ตรวจสอบ Response
  Serial.print("HTTP Response Code: ");
  Serial.println(httpCode);

  bool success = false;

  if (httpCode > 0) {
    // รับ Response Body
    String response = http.getString();
    
    if (httpCode == HTTP_CODE_OK || httpCode == 200) {
      Serial.println("✅ Data sent successfully!");
      Serial.print("Response: ");
      Serial.println(response);
      success = true;
    } else {
      Serial.println("⚠️  Server returned error");
      Serial.print("Response: ");
      Serial.println(response);
    }
  } else {
    // HTTP Request Failed
    Serial.println("❌ HTTP POST failed!");
    Serial.print("Error: ");
    Serial.println(http.errorToString(httpCode));
  }

  // ปิด Connection
  http.end();
  
  return success;
}


// ==================== Arduino Setup & Loop ====================

void setup() {
  // เริ่ม Serial Monitor
  Serial.begin(115200);
  delay(500);
  
  Serial.println("\n\n");
  Serial.println("================================================");
  Serial.println("  IoT HTTP Client - ESP32");
  Serial.println("  Virtual Sensor → FastAPI Server");
  Serial.println("================================================");
  Serial.println();

  // ตั้งค่า Random Seed
  randomSeed(micros());

  // เชื่อมต่อ Wi-Fi
  connectWiFi();

  // แสดงการตั้งค่า
  Serial.println("\n⚙️  Configuration:");
  Serial.print("Device ID: ");
  Serial.println(deviceId);
  Serial.print("Server: http://");
  Serial.print(SERVER_IP);
  Serial.print(":");
  Serial.println(SERVER_PORT);
  Serial.print("Send Interval: ");
  Serial.print(SEND_INTERVAL_MS / 1000);
  Serial.println(" seconds");
  Serial.println();

  Serial.println("🚀 ESP32 HTTP IoT Client is ready!");
  Serial.println("================================================\n");
}

void loop() {
  // ตรวจสอบ Wi-Fi Connection
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("⚠️  WiFi disconnected! Reconnecting...");
    connectWiFi();
    return;
  }

  // ตรวจสอบว่าถึงเวลาส่งข้อมูลหรือยัง
  unsigned long currentMs = millis();
  if (currentMs - lastSendMs < SEND_INTERVAL_MS) {
    return;  // ยังไม่ถึงเวลา
  }
  
  // อัปเดตเวลาส่งล่าสุด
  lastSendMs = currentMs;

  // อ่านค่า Sensor (Virtual)
  float temp = virtualTemp();
  float hum = virtualHum();

  // แสดงค่าที่อ่านได้
  Serial.println("📊 Sensor Reading:");
  Serial.print("  Temperature: ");
  Serial.print(temp, 2);
  Serial.println(" °C");
  Serial.print("  Humidity: ");
  Serial.print(hum, 2);
  Serial.println(" %");

  // ส่งข้อมูลไปยัง Server
  bool success = sendDataToServer(temp, hum);

  // แสดงสถานะ
  Serial.println();
  if (success) {
    Serial.println("✨ Cycle completed successfully!");
  } else {
    Serial.println("⚠️  Cycle completed with errors");
  }
  Serial.println("================================================\n");

  // หน่วงเวลาเล็กน้อยเพื่อให้ Serial Monitor แสดงผลได้ทัน
  delay(100);
}
