"""
FastAPI Server for IoT HTTP Workshop
=====================================
รับข้อมูลจาก IoT Device (ESP32) ผ่าน HTTP POST
และให้ endpoint สำหรับดูข้อมูลล่าสุด

Author: Workshop Materials
Date: February 2025
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

# สร้าง FastAPI application
app = FastAPI(
    title="RPi IoT Server (HTTP)",
    description="REST API สำหรับรับข้อมูลจาก IoT Devices",
    version="1.0.0"
)

# เก็บข้อมูลล่าสุดในหน่วยความจำ (In-Memory Storage)
# หมายเหตุ: ข้อมูลจะหายเมื่อ restart server
LATEST: Optional[Dict[str, Any]] = None


# ==================== Pydantic Models ====================

class SensorPayload(BaseModel):
    """
    โครงสร้างข้อมูลที่ server รับจาก IoT Device
    
    Attributes:
        device_id (str): รหัสอุปกรณ์ (เช่น esp32-01)
        temp (float): อุณหภูมิ (Celsius)
        hum (float): ความชื้นสัมพัทธ์ (%)
        source (str): แหล่งที่มาของข้อมูล (virtual/bme280/dht22)
        ts (str): timestamp (ISO format) - ถ้าไม่ส่งมา server จะใส่เอง
    """
    device_id: str
    temp: float
    hum: float
    source: Optional[str] = "unknown"
    ts: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "device_id": "esp32-01",
                "temp": 28.5,
                "hum": 65.3,
                "source": "virtual",
                "ts": "2025-02-16T10:30:00Z"
            }
        }


# ==================== API Endpoints ====================

@app.get("/")
def read_root():
    """
    Root endpoint - แสดงข้อมูลพื้นฐานของ API
    """
    return {
        "message": "RPi IoT Server is running",
        "version": "1.0.0",
        "endpoints": {
            "POST /api/data": "รับข้อมูลจาก IoT Device",
            "GET /api/latest": "ดูข้อมูลล่าสุด",
            "GET /docs": "API Documentation (Swagger UI)"
        }
    }


@app.post("/api/data")
def receive_data(payload: SensorPayload):
    """
    รับข้อมูลจาก IoT Device
    
    Args:
        payload (SensorPayload): ข้อมูล sensor ที่ส่งมา
        
    Returns:
        dict: ยืนยันการรับข้อมูลสำเร็จพร้อมข้อมูลล่าสุด
        
    Example:
        POST /api/data
        {
            "device_id": "esp32-01",
            "temp": 28.5,
            "hum": 65.3,
            "source": "virtual"
        }
    """
    global LATEST
    
    # ถ้าไม่มี timestamp ให้ server ใส่เวลา UTC ปัจจุบัน
    ts = payload.ts or datetime.utcnow().isoformat()
    
    # เก็บข้อมูลล่าสุด
    LATEST = {
        "device_id": payload.device_id,
        "temp": payload.temp,
        "hum": payload.hum,
        "source": payload.source,
        "ts": ts,
    }
    
    # แสดงใน console เพื่อ debug
    print(f"[RECV] {LATEST}")
    
    # ตอบกลับเพื่อยืนยันว่ารับข้อมูลสำเร็จ
    return {
        "ok": True,
        "message": "Data received successfully",
        "latest": LATEST
    }


@app.get("/api/latest")
def get_latest():
    """
    ดึงข้อมูลล่าสุดที่ server เก็บไว้
    
    Returns:
        dict: ข้อมูลล่าสุด
        
    Raises:
        HTTPException: 404 ถ้ายังไม่มีข้อมูลเลย
        
    Example:
        GET /api/latest
        
        Response:
        {
            "device_id": "esp32-01",
            "temp": 28.5,
            "hum": 65.3,
            "source": "virtual",
            "ts": "2025-02-16T10:30:00Z"
        }
    """
    if LATEST is None:
        raise HTTPException(
            status_code=404,
            detail="No data yet. Please send data first using POST /api/data"
        )
    
    return LATEST


@app.get("/health")
def health_check():
    """
    Health check endpoint - ตรวจสอบว่า server ยังทำงานอยู่หรือไม่
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "has_data": LATEST is not None
    }


# ==================== เพิ่ม CORS Support (สำหรับ Web Client) ====================
# Uncomment บรรทัดด้านล่างถ้าต้องการให้ Web Browser เรียก API ได้

# from fastapi.middleware.cors import CORSMiddleware
#
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # ใน production ควรระบุ domain ที่อนุญาต
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
