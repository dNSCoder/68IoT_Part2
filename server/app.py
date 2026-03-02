"""
FastAPI Server for IoT HTTP Workshop
=====================================
รับข้อมูลจาก IoT Device (Nano 33 IoT / ESP32) ผ่าน HTTP POST
และให้ endpoint สำหรับดูข้อมูลล่าสุด

โครงสร้างโฟลเดอร์:
  server/
  ├── app.py
  ├── requirements.txt
  └── templates/
      ├── index.html       ← หน้าแรก (Jinja2 template)
      └── motion_ui.html   ← Motion Dashboard (Jinja2 template)

Lesson 2 : Sensor data  (POST /api/data  |  GET /api/latest)
Lesson 4 : Motion event (POST /api/motion | GET /api/motion/latest | GET /motion)
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime, timezone
from collections import deque
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# ─────────────────────────────────────────────────────────────────
# App + Templates
# ─────────────────────────────────────────────────────────────────
app = FastAPI(
    title="RPi IoT Server",
    description="REST API สำหรับรับข้อมูลจาก IoT Devices (Nano 33 IoT / ESP32)",
    version="2.0.0",
)

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# ─────────────────────────────────────────────────────────────────
# In-Memory Storage
# ─────────────────────────────────────────────────────────────────
LATEST: Optional[Dict[str, Any]] = None     # ข้อมูล sensor ล่าสุด
MOTION_EVENTS: deque = deque(maxlen=50)     # motion events ล่าสุด 50 รายการ


# ─────────────────────────────────────────────────────────────────
# Pydantic Models
# ─────────────────────────────────────────────────────────────────
class SensorPayload(BaseModel):
    """ข้อมูล sensor จาก IoT Device (บทที่ 2-3)"""
    device_id: str
    temp: float
    hum: float
    source: Optional[str] = "unknown"
    ts: Optional[str] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "device_id": "nano33iot-01",
                "temp": 28.5,
                "hum": 65.3,
                "source": "virtual",
            }
        }
    }


class MotionPayload(BaseModel):
    """ข้อมูล motion event จาก PIR sensor (บทที่ 4)"""
    device_id: str = "nano33iot-01"
    event: str = "motion_detected"
    motion: bool = True
    rssi: Optional[int] = None
    millis: Optional[int] = None
    source: str = "pir"
    ts: Optional[str] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "device_id": "nano33iot-01",
                "event": "motion_detected",
                "motion": True,
                "rssi": -55,
                "millis": 123456,
                "source": "pir",
            }
        }
    }


# ─────────────────────────────────────────────────────────────────
# Root — หน้าแรก (Jinja2 Template)
# ─────────────────────────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """หน้าแรก — render templates/index.html ด้วย Jinja2"""
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "server_name": "RPi IoT Server",
            "version": "2.0.0",
            "endpoints": [
                {"method": "GET",  "path": "/",                   "desc": "หน้าแรก (หน้านี้)"},
                {"method": "POST", "path": "/api/data",           "desc": "รับข้อมูล sensor"},
                {"method": "GET",  "path": "/api/latest",         "desc": "ข้อมูล sensor ล่าสุด"},
                {"method": "POST", "path": "/api/motion",         "desc": "รับ motion event"},
                {"method": "GET",  "path": "/api/motion/latest",  "desc": "motion events ล่าสุด"},
                {"method": "GET",  "path": "/motion",             "desc": "Motion Dashboard"},
                {"method": "GET",  "path": "/health",             "desc": "Health check"},
                {"method": "GET",  "path": "/docs",               "desc": "Swagger UI (API Docs)"},
            ],
        },
    )


# ─────────────────────────────────────────────────────────────────
# Lesson 2-3 — Sensor Data
# ─────────────────────────────────────────────────────────────────
@app.post("/api/data")
def receive_data(payload: SensorPayload):
    """รับข้อมูล sensor จาก IoT Device"""
    global LATEST
    ts = payload.ts or datetime.now(timezone.utc).isoformat()
    LATEST = {
        "device_id": payload.device_id,
        "temp": payload.temp,
        "hum": payload.hum,
        "source": payload.source,
        "ts": ts,
    }
    print(f"[SENSOR] {LATEST}")
    return {"ok": True, "message": "Data received successfully", "latest": LATEST}


@app.get("/api/latest")
def get_latest():
    """ดึงข้อมูล sensor ล่าสุด"""
    if LATEST is None:
        raise HTTPException(status_code=404, detail="No data yet. Send data via POST /api/data first.")
    return LATEST


# ─────────────────────────────────────────────────────────────────
# Lesson 4 — Motion Detection
# ─────────────────────────────────────────────────────────────────
@app.post("/api/motion")
def receive_motion(request: Request, payload: MotionPayload):
    """รับ motion event จาก PIR sensor"""
    ts = payload.ts or datetime.now(timezone.utc).isoformat()
    ip = request.client.host if request.client else "unknown"
    item = {
        "ts": ts,
        "device_id": payload.device_id,
        "event": payload.event,
        "motion": payload.motion,
        "rssi": payload.rssi,
        "millis": payload.millis,
        "source": payload.source,
        "ip": ip,
    }
    MOTION_EVENTS.appendleft(item)
    print(f"[MOTION] {item}")
    return {"ok": True, "item": item}


@app.get("/api/motion/latest")
def motion_latest(limit: int = 20):
    """ดึง motion events ล่าสุด"""
    n = max(1, min(limit, len(MOTION_EVENTS))) if MOTION_EVENTS else 0
    return {"items": list(MOTION_EVENTS)[:n]}


@app.get("/motion", response_class=HTMLResponse)
async def motion_page(request: Request):
    """Motion Dashboard — render templates/motion_ui.html ด้วย Jinja2 (server-side)"""
    latest = MOTION_EVENTS[0] if MOTION_EVENTS else None
    return templates.TemplateResponse(
        request=request,
        name="motion_ui.html",
        context={
            "items": list(MOTION_EVENTS),
            "latest": latest,
            "total": len(MOTION_EVENTS),
            "detected_count": sum(1 for e in MOTION_EVENTS if e["motion"] is True),
            "stopped_count":  sum(1 for e in MOTION_EVENTS if e["motion"] is False),
        },
    )


# ─────────────────────────────────────────────────────────────────
# Health Check
# ─────────────────────────────────────────────────────────────────
@app.get("/health")
def health_check():
    """ตรวจสอบสถานะ server"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "sensor_data": LATEST is not None,
        "motion_events": len(MOTION_EVENTS),
    }
