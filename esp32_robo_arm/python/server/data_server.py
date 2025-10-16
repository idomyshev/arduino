#!/usr/bin/env python3
"""
Robot Arm Data Server
Простой сервер для хранения калибровочных данных и позиций робота
"""

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
active_connections = set()  # WebSocket соединения

# WebSocket для управления роботом
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint для управления роботом"""
    global robot_connected
    await websocket.accept()
    active_connections.add(websocket)
    
    try:
        while True:
            # Получаем сообщение от клиента
            data = await websocket.receive_text()
            print(f"WebSocket: Получено сообщение: {data}")
            message = json.loads(data)
            print(f"WebSocket: Распарсенное сообщение: {message}")
            
            # Обрабатываем команды
            command = message.get("command")
            print(f"WebSocket: Команда: {command}")
            
            if command == "connect":
                # Подключение к роботу
                print(f"WebSocket: Получена команда connect")
                try:
                    device = await robot_controller.scan_for_device()
                    print(f"WebSocket: Результат сканирования: {device}")
                    if device:
                        print(f"WebSocket: Попытка подключения к {device.name}")
                        success = await robot_controller.connect(device)
                        print(f"WebSocket: Результат подключения: {success}")
                        if success:
                            robot_connected = True
                            response = {
                                "type": "connection_status",
                                "connected": True,
                                "message": f"Подключено к {device.name}"
                            }
                            print(f"WebSocket: Отправка ответа: {response}")
                            await websocket.send_text(json.dumps(response))
                        else:
                            response = {
                                "type": "connection_status", 
                                "connected": False,
                                "message": "Ошибка подключения к роботу"
                            }
                            print(f"WebSocket: Отправка ответа: {response}")
                            await websocket.send_text(json.dumps(response))
                    else:
                        response = {
                            "type": "connection_status",
                            "connected": False, 
                            "message": "Робот не найден. Убедитесь, что он включен и в зоне действия Bluetooth"
                        }
                        print(f"WebSocket: Отправка ответа: {response}")
                        await websocket.send_text(json.dumps(response))
                except Exception as e:
                    print(f"WebSocket: Ошибка в команде connect: {e}")
                    response = {
                        "type": "error",
                        "message": f"Ошибка подключения: {str(e)}"
                    }
                    await websocket.send_text(json.dumps(response))
            
            elif command == "disconnect":
                # Отключение от робота
                await robot_controller.disconnect()
                robot_connected = False
                await websocket.send_text(json.dumps({
                    "type": "connection_status",
                    "connected": False,
                    "message": "Отключено от робота"
                }))
            
            elif command == "move_motor":
                # Движение мотора
                if not robot_connected:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": "Сначала подключитесь к роботу!"
                    }))
                    continue
                
                motor = message.get("motor")
                direction = message.get("direction")
                speed = message.get("speed")
                duration = message.get("duration")
                
                try:
                    await robot_controller.send_command(motor, direction, speed, duration)
                    await websocket.send_text(json.dumps({
                        "type": "motor_command",
                        "success": True,
                        "message": f"Мотор {motor} {direction} со скоростью {speed}"
                    }))
                except Exception as e:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": f"Ошибка команды мотора: {str(e)}"
                    }))
            
            elif command == "stop_motor":
                # Остановка мотора
                if not robot_connected:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": "Сначала подключитесь к роботу!"
                    }))
                    continue
                
                motor = message.get("motor")
                try:
                    await robot_controller.send_command(motor, "stop", 0)
                    await websocket.send_text(json.dumps({
                        "type": "motor_command",
                        "success": True,
                        "message": f"Мотор {motor} остановлен"
                    }))
                except Exception as e:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": f"Ошибка остановки мотора: {str(e)}"
                    }))
            
            elif command == "stop_all":
                # Остановка всех моторов
                if not robot_connected:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": "Сначала подключитесь к роботу!"
                    }))
                    continue
                
                try:
                    await robot_controller.stop_all_motors()
                    await websocket.send_text(json.dumps({
                        "type": "motor_command",
                        "success": True,
                        "message": "Все моторы остановлены"
                    }))
                except Exception as e:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": f"Ошибка остановки моторов: {str(e)}"
                    }))
            
            elif command == "get_status":
                # Получение статуса
                print(f"WebSocket: Получена команда get_status, robot_connected = {robot_connected}")
                await websocket.send_text(json.dumps({
                    "type": "status",
                    "robot_connected": robot_connected,
                    "active_connections": len(active_connections)
                }))
            
            else:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": f"Неизвестная команда: {command}"
                }))
    
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
