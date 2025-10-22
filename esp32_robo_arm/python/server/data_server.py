#!/usr/bin/env python3
from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Dict, Optional, List
from contextlib import asynccontextmanager
import json
import os
import sqlite3
from datetime import datetime
import uvicorn
import asyncio
import sys

# Добавляем путь к модулям робота
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from classes.robot_arm_controller import RobotArmController

# Lifespan функция для управления жизненным циклом приложения
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_database()
    print("Robot Arm Data Server started!")
    print("Database initialized at:", DB_PATH)
    print("Web interface available at: http://localhost:8000/")
    print("Calibration page: http://localhost:8000/calibration")
    yield
    # Shutdown
    print("Shutting down server...")

app = FastAPI(title="Robot Arm Data Server", version="1.0.0", lifespan=lifespan)

# База данных
DB_PATH = os.path.join(os.path.dirname(__file__), "robot_data_server.db")

# Глобальный контроллер робота
robot_controller = RobotArmController()
robot_connected = False
active_connections = set()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint для управления роботом"""
    global robot_connected
    await websocket.accept()
    active_connections.add(websocket)

    known_commands = ["connect", "disconnect", "move_motor", "stop_motor", "stop_all", "status"]
    check_connection_commands = ["move_motor", "stop_motor", "stop_all"]

    command_error = None
    error = None
    message = None
    
    try:
        while True:
            data_not_parsed = await websocket.receive_text()
            data = json.loads(data_not_parsed)
            print(f"Get message from websocket: {data}")
            
            command = data.get("command")
            
            if not command:
                await websocket.send_text(json.dumps({
                    "error": True,
                    "message": "Command is required but not provided"
                }))

            if command not in known_commands:
                await websocket.send_text(json.dumps({
                    "error": True,
                    "message": f"Unknown command: {command}. Available commands: {', '.join(known_commands)}"
                }))

            if command == "status":
                error = False
                message = f"Active websocket connections number: {len(active_connections)}"

            elif command == "connect":
                try:
                    device = await robot_controller.scan_for_device()

                    if device:
                        success = await robot_controller.connect(device)

                        if success:
                            error = False
                            message = f"Connected to {device.name}"

                        else:
                            error = True
                            message = "Error to connect to robot"
                    else:
                        error = True
                        message = "Robot not found via bluetooth"

                except Exception as e:
                    error = True
                    message = f"Error in websocket command"
                    command_error = e
            
            elif command == "disconnect":
                await robot_controller.disconnect()
                robot_connected = False
                error = False
                message = "Disconnected from robot"

            # This check should be before other checks which depend on this one
            elif command in check_connection_commands:
                await websocket.send_text(json.dumps({
                        "error": True,
                        command: command,
                        "message": "Robot should be connected to use this command"
                    }))
                continue
            
            elif command == "move_motor":
                motor = message.get("motor")
                direction = message.get("direction")
                speed = message.get("speed")
                duration = message.get("duration")
                
                try:
                    error = False
                    message = f"Motor {motor}, direction {direction}, speed {speed}, duration {duration}"
                except Exception as e:
                    error = True
                    message = f"Error move motor {motor}, direction {direction}, speed {speed}, duration {duration}"
                    command_error = e
            
            elif command == "stop_motor":
                motor = message.get("motor")

                try:
                    error = False
                    message = f"Motor {motor} stopped"
                except Exception as e:
                    error = True
                    message = f"Error stop motor {motor} stopped"
                    command_error = e
            
            elif command == "stop_all":
                try:
                    await robot_controller.stop_all_motors()
                    error = False
                    message = f"All motors stopped"

                except Exception as e:
                    error = True
                    message = f"Error stop all motors"
                    command_error = e
            
            response = {
                "error": error,
                "command": command,
                "message": message,
                "robot_connected": robot_connected
            }
            
            if command_error is not None and error:
                response["command_error"] = str(command_error)

            print(f"WebSocket response: {response}")        
        
            await websocket.send_text(json.dumps(response))
    
    except WebSocketDisconnect:
        active_connections.discard(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        active_connections.discard(websocket)

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

@app.get("/api")
async def api_info():
    """Информация о всех доступных API endpoints"""
    base_url = "http://localhost:8000"
    
    endpoints = {
        "info": {
            "title": "Robot Arm Data Server API",
            "version": "1.0.0",
            "description": "API для управления данными робота-руки ESP32",
            "base_url": base_url
        },
        "endpoints": {
            "calibration": {
                "save": {
                    "method": "POST",
                    "url": f"{base_url}/api/calibration",
                    "description": "Сохранение калибровочных данных робота",
                    "body": "CalibrationRequest"
                },
                "get": {
                    "method": "GET", 
                    "url": f"{base_url}/api/calibration/{{robot_id}}",
                    "description": "Получение калибровочных данных робота",
                    "example": f"{base_url}/api/calibration/esp32_robot_arm_001"
                }
            },
            "position": {
                "save": {
                    "method": "POST",
                    "url": f"{base_url}/api/position",
                    "description": "Сохранение текущей позиции робота",
                    "body": "PositionRequest"
                },
                "get": {
                    "method": "GET",
                    "url": f"{base_url}/api/position/{{robot_id}}",
                    "description": "Получение текущей позиции робота",
                    "example": f"{base_url}/api/position/esp32_robot_arm_001"
                },
                "history": {
                    "method": "GET",
                    "url": f"{base_url}/api/position/{{robot_id}}/history",
                    "description": "Получение истории позиций робота",
                    "example": f"{base_url}/api/position/esp32_robot_arm_001/history"
                }
            },
            "management": {
                "robots": {
                    "method": "GET",
                    "url": f"{base_url}/api/robots",
                    "description": "Получение списка всех роботов"
                },
                "status": {
                    "method": "GET",
                    "url": f"{base_url}/api/status",
                    "description": "Статус сервера"
                },
                "database": {
                    "method": "GET",
                    "url": f"{base_url}/api/database",
                    "description": "Структура базы данных"
                },
                "api_info": {
                    "method": "GET",
                    "url": f"{base_url}/api",
                    "description": "Информация о всех endpoints (этот endpoint)"
                }
            }
        },
        "data_models": {
            "CalibrationRequest": {
                "robot_id": "string",
                "calibration_data": "Dict[str, MotorCalibrationData]"
            },
            "PositionRequest": {
                "robot_id": "string", 
                "position": "RobotPosition"
            },
            "MotorCalibrationData": {
                "motor_id": "int",
                "calibrated": "bool",
                "calibration_date": "string",
                "forward_time": "float",
                "backward_time": "float",
                "speed": "int",
                "min_position": "float (optional)",
                "max_position": "float (optional)",
                "return_time": "float (optional)",
                "total_travel_time": "float (optional)",
                "average_travel_time": "float (optional)"
            },
            "RobotPosition": {
                "timestamp": "string",
                "motor_positions": "Dict[int, float]",
                "position_name": "string (optional)"
            }
        }
    }
    
    return endpoints

@app.get("/api/database")
async def database_info():
    """Информация о структуре базы данных"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Получаем список всех таблиц
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        database_info = {
            "database_path": DB_PATH,
            "tables": {}
        }
        
        for table in tables:
            table_name = table[0]
            
            # Получаем структуру таблицы
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            
            # Получаем количество записей
            cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
            count = cursor.fetchone()[0]
            
            # Получаем примеры данных (первые 3 записи)
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 3;")
            sample_data = cursor.fetchall()
            
            # Получаем названия колонок
            column_names = [col[1] for col in columns]
            
            database_info["tables"][table_name] = {
                "columns": [
                    {
                        "name": col[1],
                        "type": col[2],
                        "not_null": bool(col[3]),
                        "default_value": col[4],
                        "primary_key": bool(col[5])
                    }
                    for col in columns
                ],
                "row_count": count,
                "sample_data": [
                    dict(zip(column_names, row)) for row in sample_data
                ]
            }
        
        conn.close()
        
        return database_info
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
