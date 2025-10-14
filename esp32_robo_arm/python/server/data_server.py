#!/usr/bin/env python3
"""
Robot Arm Data Server
Простой сервер для хранения калибровочных данных и позиций робота
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional, List
import json
import os
import sqlite3
from datetime import datetime
import uvicorn

app = FastAPI(title="Robot Arm Data Server", version="1.0.0")

# База данных
DB_PATH = os.path.join(os.path.dirname(__file__), "robot_data_server.db")

# Модели данных
class MotorCalibrationData(BaseModel):
    motor_id: int
    calibrated: bool
    calibration_date: str
    forward_time: float
    backward_time: float
    speed: int
    min_position: Optional[float] = None
    max_position: Optional[float] = None
    return_time: Optional[float] = None
    total_travel_time: Optional[float] = None
    average_travel_time: Optional[float] = None

class RobotPosition(BaseModel):
    timestamp: str
    motor_positions: Dict[int, float]
    position_name: Optional[str] = None

class CalibrationRequest(BaseModel):
    robot_id: str
    calibration_data: Dict[str, MotorCalibrationData]

class PositionRequest(BaseModel):
    robot_id: str
    position: RobotPosition

# Инициализация базы данных
def init_database():
    """Инициализация базы данных сервера"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Таблица калибровочных данных
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS motor_calibration (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            robot_id TEXT NOT NULL,
            motor_id INTEGER NOT NULL,
            calibrated BOOLEAN NOT NULL,
            calibration_date TEXT NOT NULL,
            forward_time REAL NOT NULL,
            backward_time REAL NOT NULL,
            speed INTEGER NOT NULL,
            min_position REAL,
            max_position REAL,
            return_time REAL,
            total_travel_time REAL,
            average_travel_time REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(robot_id, motor_id)
        )
    ''')
    
    # Таблица позиций
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS robot_positions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            robot_id TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            motor_positions TEXT NOT NULL,
            position_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
    
    # Таблица состояний робота
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS robot_states (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            robot_id TEXT NOT NULL,
            last_update TEXT NOT NULL,
            is_connected BOOLEAN NOT NULL,
            current_position TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(robot_id)
        )
    ''')
    
    conn.commit()
    conn.close()

# API эндпоинты
@app.post("/api/calibration")
async def save_calibration(request: CalibrationRequest):
    """Сохранение калибровочных данных"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        for motor_id_str, calib_data in request.calibration_data.items():
            motor_id = int(motor_id_str)
            cursor.execute('''
                INSERT OR REPLACE INTO motor_calibration 
                (robot_id, motor_id, calibrated, calibration_date, forward_time, 
                 backward_time, speed, min_position, max_position, return_time, 
                 total_travel_time, average_travel_time, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                request.robot_id, motor_id, calib_data.calibrated,
                calib_data.calibration_date, calib_data.forward_time,
                calib_data.backward_time, calib_data.speed,
                calib_data.min_position, calib_data.max_position,
                calib_data.return_time, calib_data.total_travel_time,
                calib_data.average_travel_time, datetime.now().isoformat()
            ))
        
        conn.commit()
        conn.close()
        
        return {"status": "success", "message": "Calibration data saved"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/calibration/{robot_id}")
async def get_calibration(robot_id: str):
    """Получение калибровочных данных"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT motor_id, calibrated, calibration_date, forward_time,
                   backward_time, speed, min_position, max_position,
                   return_time, total_travel_time, average_travel_time
            FROM motor_calibration 
            WHERE robot_id = ?
        ''', (robot_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        calibration_data = {}
        for row in rows:
            motor_id = row[0]
            calibration_data[str(motor_id)] = MotorCalibrationData(
                motor_id=motor_id,
                calibrated=row[1],
                calibration_date=row[2],
                forward_time=row[3],
                backward_time=row[4],
                speed=row[5],
                min_position=row[6],
                max_position=row[7],
                return_time=row[8],
                total_travel_time=row[9],
                average_travel_time=row[10]
            )
        
        return {"robot_id": robot_id, "calibration_data": calibration_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/position")
async def save_position(request: PositionRequest):
    """Сохранение текущей позиции"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Сохраняем историю позиций
        cursor.execute('''
            INSERT INTO robot_positions 
            (robot_id, timestamp, motor_positions, position_name)
            VALUES (?, ?, ?, ?)
        ''', (
            request.robot_id, request.position.timestamp,
            json.dumps(request.position.motor_positions), request.position.position_name
        ))
        
        # Обновляем текущее состояние
        cursor.execute('''
            INSERT OR REPLACE INTO robot_states 
            (robot_id, last_update, is_connected, current_position)
            VALUES (?, ?, ?, ?)
        ''', (
            request.robot_id, request.position.timestamp, True,
            json.dumps(request.position.model_dump())
        ))
        
        conn.commit()
        conn.close()
        
        return {"status": "success", "message": "Position saved"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/position/{robot_id}")
async def get_position(robot_id: str):
    """Получение текущей позиции"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT current_position FROM robot_states 
            WHERE robot_id = ?
        ''', (robot_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            position_data = json.loads(row[0])
            return {"robot_id": robot_id, "position": position_data}
        else:
            raise HTTPException(status_code=404, detail="Position not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/position/{robot_id}/history")
async def get_position_history(robot_id: str, limit: int = 100):
    """Получение истории позиций"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT timestamp, motor_positions, position_name
            FROM robot_positions 
            WHERE robot_id = ?
            ORDER BY created_at DESC
            LIMIT ?
        ''', (robot_id, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        positions = []
        for row in rows:
            positions.append({
                "timestamp": row[0],
                "motor_positions": json.loads(row[1]),
                "position_name": row[2]
            })
        
        return {"robot_id": robot_id, "positions": positions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/robots")
async def list_robots():
    """Получение списка всех роботов"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT DISTINCT robot_id FROM robot_states
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        robots = [row[0] for row in rows]
        return {"robots": robots}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/status")
async def server_status():
    """Статус сервера"""
    return {
        "status": "running",
        "version": "1.0.0",
        "database": DB_PATH,
        "timestamp": datetime.now().isoformat()
    }

# Инициализация при запуске
@app.on_event("startup")
async def startup_event():
    init_database()
    print("Robot Arm Data Server started!")
    print("Database initialized at:", DB_PATH)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
