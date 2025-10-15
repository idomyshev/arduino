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

# Веб-страницы
@app.get("/", response_class=HTMLResponse)
async def home_page():
    """Домашняя страница робота"""
    return """
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>ESP32 Robot Arm Control</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                min-height: 100vh;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 20px;
                padding: 40px;
                backdrop-filter: blur(10px);
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            }
            h1 {
                text-align: center;
                font-size: 3em;
                margin-bottom: 10px;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
            }
            .subtitle {
                text-align: center;
                font-size: 1.2em;
                margin-bottom: 40px;
                opacity: 0.9;
            }
            .features {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 30px;
                margin: 40px 0;
            }
            .feature-card {
                background: rgba(255, 255, 255, 0.15);
                border-radius: 15px;
                padding: 30px;
                text-align: center;
                transition: transform 0.3s ease;
            }
            .feature-card:hover {
                transform: translateY(-5px);
            }
            .feature-icon {
                font-size: 3em;
                margin-bottom: 20px;
            }
            .feature-title {
                font-size: 1.5em;
                margin-bottom: 15px;
                font-weight: bold;
            }
            .feature-description {
                opacity: 0.9;
                line-height: 1.6;
            }
            .actions {
                text-align: center;
                margin: 40px 0;
            }
            .btn {
                display: inline-block;
                padding: 15px 30px;
                margin: 10px;
                background: rgba(255, 255, 255, 0.2);
                color: white;
                text-decoration: none;
                border-radius: 25px;
                font-size: 1.1em;
                font-weight: bold;
                transition: all 0.3s ease;
                border: 2px solid rgba(255, 255, 255, 0.3);
            }
            .btn:hover {
                background: rgba(255, 255, 255, 0.3);
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
            }
            .btn-primary {
                background: rgba(76, 175, 80, 0.8);
                border-color: rgba(76, 175, 80, 1);
            }
            .btn-primary:hover {
                background: rgba(76, 175, 80, 1);
            }
            .status {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                padding: 20px;
                margin: 20px 0;
                text-align: center;
            }
            .status-indicator {
                display: inline-block;
                width: 12px;
                height: 12px;
                border-radius: 50%;
                background: #4CAF50;
                margin-right: 10px;
                animation: pulse 2s infinite;
            }
            @keyframes pulse {
                0% { opacity: 1; }
                50% { opacity: 0.5; }
                100% { opacity: 1; }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 ESP32 Robot Arm</h1>
            <p class="subtitle">Система управления роботом-рукой через веб-интерфейс</p>
            
            <div class="status">
                <span class="status-indicator"></span>
                <strong>Сервер активен</strong> - API работает на порту 8000
            </div>
            
            <div class="features">
                <div class="feature-card">
                    <div class="feature-icon">🎯</div>
                    <div class="feature-title">Точная калибровка</div>
                    <div class="feature-description">
                        Автоматическая калибровка моторов с ручным приведением к стартовой позиции.
                        Определение времени движения вперед и назад для каждого мотора.
                    </div>
                </div>
                
                <div class="feature-card">
                    <div class="feature-icon">📡</div>
                    <div class="feature-title">Bluetooth управление</div>
                    <div class="feature-description">
                        Беспроводное управление через Bluetooth Low Energy (BLE).
                        Подключение к ESP32 роботу без проводов.
                    </div>
                </div>
                
                <div class="feature-card">
                    <div class="feature-icon">💾</div>
                    <div class="feature-title">Централизованное хранение</div>
                    <div class="feature-description">
                        Все данные калибровки и позиций сохраняются в централизованной базе данных.
                        API для интеграции с другими системами.
                    </div>
                </div>
                
                <div class="feature-card">
                    <div class="feature-icon">🔄</div>
                    <div class="feature-title">Автоматическое восстановление</div>
                    <div class="feature-description">
                        Система автоматически загружает калибровочные данные и стартовые позиции
                        при подключении к роботу.
                    </div>
                </div>
            </div>
            
            <div class="actions">
                <a href="/calibration" class="btn btn-primary">🎯 Калибровка робота</a>
                <a href="/api" class="btn">📚 API Документация</a>
                <a href="/api/database" class="btn">🗄️ База данных</a>
                <a href="/api/status" class="btn">📊 Статус сервера</a>
            </div>
            
            <div class="status">
                <h3>🚀 Быстрый старт:</h3>
                <p>1. Убедитесь, что ESP32 робот включен и находится в зоне действия Bluetooth</p>
                <p>2. Нажмите "Калибровка робота" для начала процесса</p>
                <p>3. Следуйте инструкциям на экране</p>
            </div>
        </div>
    </body>
    </html>
    """

@app.get("/calibration", response_class=HTMLResponse)
async def calibration_page():
    """Страница калибровки робота"""
    return """
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Калибровка робота - ESP32 Robot Arm</title>
        <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
        <meta http-equiv="Pragma" content="no-cache">
        <meta http-equiv="Expires" content="0">
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                min-height: 100vh;
            }
            .container {
                max-width: 1000px;
                margin: 0 auto;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 20px;
                padding: 40px;
                backdrop-filter: blur(10px);
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            }
            h1 {
                text-align: center;
                font-size: 2.5em;
                margin-bottom: 10px;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
            }
            .subtitle {
                text-align: center;
                font-size: 1.1em;
                margin-bottom: 40px;
                opacity: 0.9;
            }
            .step {
                background: rgba(255, 255, 255, 0.15);
                border-radius: 15px;
                padding: 30px;
                margin: 20px 0;
                border-left: 5px solid #4CAF50;
            }
            .step-title {
                font-size: 1.3em;
                font-weight: bold;
                margin-bottom: 15px;
                color: #4CAF50;
            }
            .step-content {
                line-height: 1.6;
            }
            .btn {
                display: inline-block;
                padding: 12px 25px;
                margin: 10px 5px;
                background: rgba(255, 255, 255, 0.2);
                color: white;
                text-decoration: none;
                border-radius: 25px;
                font-size: 1em;
                font-weight: bold;
                transition: all 0.3s ease;
                border: 2px solid rgba(255, 255, 255, 0.3);
                cursor: pointer;
            }
            .btn:hover {
                background: rgba(255, 255, 255, 0.3);
                transform: translateY(-2px);
            }
            .btn-primary {
                background: rgba(76, 175, 80, 0.8);
                border-color: rgba(76, 175, 80, 1);
            }
            .btn-primary:hover {
                background: rgba(76, 175, 80, 1);
            }
            .btn-danger {
                background: rgba(244, 67, 54, 0.8);
                border-color: rgba(244, 67, 54, 1);
            }
            .btn-danger:hover {
                background: rgba(244, 67, 54, 1);
            }
            .motor-control {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                padding: 20px;
                margin: 15px 0;
            }
            .motor-title {
                font-size: 1.2em;
                font-weight: bold;
                margin-bottom: 15px;
                color: #FFC107;
            }
            .control-group {
                display: flex;
                gap: 10px;
                align-items: center;
                margin: 10px 0;
                flex-wrap: wrap;
            }
            .control-group label {
                min-width: 100px;
                font-weight: bold;
            }
            .control-group input, .control-group select {
                padding: 8px 12px;
                border-radius: 5px;
                border: 1px solid rgba(255, 255, 255, 0.3);
                background: rgba(255, 255, 255, 0.1);
                color: white;
            }
            .status-indicator {
                display: inline-block;
                width: 12px;
                height: 12px;
                border-radius: 50%;
                margin-right: 10px;
            }
            .status-connected {
                background: #4CAF50;
                animation: pulse 2s infinite;
            }
            .status-disconnected {
                background: #F44336;
            }
            @keyframes pulse {
                0% { opacity: 1; }
                50% { opacity: 0.5; }
                100% { opacity: 1; }
            }
            .warning {
                background: rgba(255, 193, 7, 0.2);
                border: 1px solid rgba(255, 193, 7, 0.5);
                border-radius: 10px;
                padding: 15px;
                margin: 20px 0;
            }
            .warning-title {
                font-weight: bold;
                color: #FFC107;
                margin-bottom: 10px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎯 Калибровка робота</h1>
            <p class="subtitle">Пошаговая калибровка моторов ESP32 робота-руки</p>
            
            <div class="step">
                <div class="step-title">📡 Шаг 1: Подключение к роботу</div>
                <div class="step-content">
                    <p>Убедитесь, что ESP32 робот включен и находится в зоне действия Bluetooth.</p>
                    <div class="control-group">
                        <span class="status-indicator status-disconnected" id="connection-status"></span>
                        <span id="connection-text">Не подключено</span>
                        <button class="btn btn-primary" onclick="connectToRobot()">Подключиться</button>
                    </div>
                </div>
            </div>
            
            <div class="step">
                <div class="step-title">🏠 Шаг 2: Приведение к стартовой позиции</div>
                <div class="step-content">
                    <p><strong>НОВОЕ:</strong> Ручное приведение каждого мотора к стартовой позиции (0%).</p>
                    <p>Это позволяет точно определить стартовую точку без использования третьего временного параметра.</p>
                    
                    <div class="motor-control">
                        <div class="motor-title">Малое плечо (M1)</div>
                        <div class="control-group">
                            <button class="btn btn-primary" onclick="moveMotor(0, 'backward')">Опустить</button>
                            <button class="btn btn-primary" onclick="moveMotor(0, 'forward')">Поднять</button>
                            <button class="btn btn-danger" onclick="stopMotor(0)">Стоп</button>
                            <span>Позиция: <span id="motor-0-position">0%</span></span>
                        </div>
                        <div class="control-group">
                            <label>Скорость:</label>
                            <input type="range" id="speed-0" min="50" max="255" value="200" onchange="updateSpeed(0)">
                            <span id="speed-value-0">200</span>
                        </div>
                        <div class="control-group">
                            <button class="btn btn-primary" onclick="setStartPosition(0)">✅ Установить стартовую позицию</button>
                        </div>
                    </div>
                    
                    <div class="motor-control">
                        <div class="motor-title">Большое плечо (M2)</div>
                        <div class="control-group">
                            <button class="btn btn-primary" onclick="moveMotor(1, 'backward')">Поднять</button>
                            <button class="btn btn-primary" onclick="moveMotor(1, 'forward')">Опустить</button>
                            <button class="btn btn-danger" onclick="stopMotor(1)">Стоп</button>
                            <span>Позиция: <span id="motor-1-position">0%</span></span>
                        </div>
                        <div class="control-group">
                            <label>Скорость:</label>
                            <input type="range" id="speed-1" min="50" max="255" value="200" onchange="updateSpeed(1)">
                            <span id="speed-value-1">200</span>
                        </div>
                        <div class="control-group">
                            <button class="btn btn-primary" onclick="setStartPosition(1)">✅ Установить стартовую позицию</button>
                        </div>
                    </div>
                    
                    <div class="motor-control">
                        <div class="motor-title">Клешня (M3)</div>
                        <div class="control-group">
                            <button class="btn btn-primary" onclick="moveMotor(2, 'backward')">Закрыть</button>
                            <button class="btn btn-primary" onclick="moveMotor(2, 'forward')">Открыть</button>
                            <button class="btn btn-danger" onclick="stopMotor(2)">Стоп</button>
                            <span>Позиция: <span id="motor-2-position">0%</span></span>
                        </div>
                        <div class="control-group">
                            <label>Скорость:</label>
                            <input type="range" id="speed-2" min="50" max="255" value="200" onchange="updateSpeed(2)">
                            <span id="speed-value-2">200</span>
                        </div>
                        <div class="control-group">
                            <button class="btn btn-primary" onclick="setStartPosition(2)">✅ Установить стартовую позицию</button>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="step">
                <div class="step-title">⏱️ Шаг 3: Измерение времени движения</div>
                <div class="step-content">
                    <p>После установки стартовых позиций измерьте время движения каждого мотора:</p>
                    <div class="warning">
                        <div class="warning-title">⚠️ Важно:</div>
                        <p>Теперь нам нужны только 2 параметра для каждого мотора:</p>
                        <ul>
                            <li><strong>forward_time</strong> - время движения вперед до упора</li>
                            <li><strong>backward_time</strong> - время движения назад до стартовой позиции</li>
                        </ul>
                        <p>Третий параметр (return_time) больше не нужен!</p>
                    </div>
                    
                    <div class="motor-control">
                        <div class="motor-title">Измерение времени для Малое плечо (M1)</div>
                        <div class="control-group">
                            <button class="btn btn-primary" onclick="measureForwardTime(0)">⏱️ Измерить время вперед</button>
                            <span>Время вперед: <span id="forward-time-0">-</span> сек</span>
                        </div>
                        <div class="control-group">
                            <button class="btn btn-primary" onclick="measureBackwardTime(0)">⏱️ Измерить время назад</button>
                            <span>Время назад: <span id="backward-time-0">-</span> сек</span>
                        </div>
                    </div>
                    
                    <div class="motor-control">
                        <div class="motor-title">Измерение времени для Большое плечо (M2)</div>
                        <div class="control-group">
                            <button class="btn btn-primary" onclick="measureForwardTime(1)">⏱️ Измерить время вперед</button>
                            <span>Время вперед: <span id="forward-time-1">-</span> сек</span>
                        </div>
                        <div class="control-group">
                            <button class="btn btn-primary" onclick="measureBackwardTime(1)">⏱️ Измерить время назад</button>
                            <span>Время назад: <span id="backward-time-1">-</span> сек</span>
                        </div>
                    </div>
                    
                    <div class="motor-control">
                        <div class="motor-title">Измерение времени для Клешня (M3)</div>
                        <div class="control-group">
                            <button class="btn btn-primary" onclick="measureForwardTime(2)">⏱️ Измерить время вперед</button>
                            <span>Время вперед: <span id="forward-time-2">-</span> сек</span>
                        </div>
                        <div class="control-group">
                            <button class="btn btn-primary" onclick="measureBackwardTime(2)">⏱️ Измерить время назад</button>
                            <span>Время назад: <span id="backward-time-2">-</span> сек</span>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="step">
                <div class="step-title">💾 Шаг 4: Сохранение калибровки</div>
                <div class="step-content">
                    <p>Сохраните все калибровочные данные в базу данных:</p>
                    <div class="control-group">
                        <button class="btn btn-primary" onclick="saveCalibration()">💾 Сохранить калибровку</button>
                        <button class="btn btn-primary" onclick="saveStartPosition()">🏠 Сохранить стартовую позицию</button>
                    </div>
                </div>
            </div>
            
            <div class="actions" style="text-align: center; margin-top: 40px;">
                <a href="/" class="btn">🏠 На главную</a>
                <button class="btn btn-danger" onclick="disconnectRobot()">🔌 Отключиться</button>
            </div>
        </div>
        
        <script>
            let robotConnected = false;
            let motorPositions = [0, 0, 0];
            let calibrationData = {};
            let websocket = null;
            let measurementTimers = {};
            
            // Подключение к WebSocket
            function connectWebSocket() {
                const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                const wsUrl = `${protocol}//${window.location.host}/ws`;
                
                console.log('Попытка подключения к WebSocket:', wsUrl);
                
                try {
                    websocket = new WebSocket(wsUrl);
                } catch (error) {
                    console.error('Ошибка создания WebSocket:', error);
                    alert('Ошибка создания WebSocket соединения');
                    return;
                }
                
                websocket.onopen = function(event) {
                    console.log('WebSocket подключен успешно');
                    // Запрашиваем текущий статус
                    websocket.send(JSON.stringify({command: 'get_status'}));
                };
                
                websocket.onmessage = function(event) {
                    const data = JSON.parse(event.data);
                    console.log('Получено сообщение:', data);
                    
                    if (data.type === 'connection_status') {
                        robotConnected = data.connected;
                        updateConnectionStatus(data.connected, data.message);
                    } else if (data.type === 'error') {
                        alert(`Ошибка: ${data.message}`);
                    } else if (data.type === 'motor_command') {
                        console.log(`Команда выполнена: ${data.message}`);
                    } else if (data.type === 'status') {
                        robotConnected = data.robot_connected;
                        updateConnectionStatus(data.robot_connected, 
                            data.robot_connected ? 'Подключено' : 'Не подключено');
                    }
                };
                
                websocket.onclose = function(event) {
                    console.log('WebSocket отключен. Код:', event.code, 'Причина:', event.reason);
                    robotConnected = false;
                    updateConnectionStatus(false, 'Соединение потеряно');
                    
                    // Попытка переподключения через 3 секунды
                    setTimeout(() => {
                        console.log('Попытка переподключения...');
                        connectWebSocket();
                    }, 3000);
                };
                
                websocket.onerror = function(error) {
                    console.error('WebSocket ошибка:', error);
                    console.log('WebSocket readyState:', websocket.readyState);
                    alert('Ошибка соединения с сервером. Проверьте, что сервер запущен на порту 8000.');
                };
            }
            
            function updateConnectionStatus(connected, message) {
                const statusElement = document.getElementById('connection-status');
                const textElement = document.getElementById('connection-text');
                
                if (connected) {
                    statusElement.className = 'status-indicator status-connected';
                    textElement.textContent = message;
                } else {
                    statusElement.className = 'status-indicator status-disconnected';
                    textElement.textContent = message;
                }
            }
            
            function connectToRobot() {
                if (!websocket || websocket.readyState !== WebSocket.OPEN) {
                    alert('WebSocket не подключен. Перезагрузите страницу.');
                    return;
                }
                
                websocket.send(JSON.stringify({command: 'connect'}));
            }
            
            function disconnectRobot() {
                if (!websocket || websocket.readyState !== WebSocket.OPEN) {
                    return;
                }
                
                websocket.send(JSON.stringify({command: 'disconnect'}));
            }
            
            function moveMotor(motor, direction, speed) {
                if (!robotConnected) {
                    alert('Сначала подключитесь к роботу!');
                    return;
                }
                
                if (!websocket || websocket.readyState !== WebSocket.OPEN) {
                    alert('WebSocket не подключен');
                    return;
                }
                
                // Если скорость не передана, получаем её из ползунка
                if (speed === undefined) {
                    speed = parseInt(document.getElementById(`speed-${motor}`).value);
                    console.log(`Получена скорость из ползунка ${motor}: ${speed}`);
                } else {
                    console.log(`Используется переданная скорость: ${speed}`);
                }
                
                console.log(`Отправка команды: мотор=${motor}, направление=${direction}, скорость=${speed}`);
                
                websocket.send(JSON.stringify({
                    command: 'move_motor',
                    motor: motor,
                    direction: direction,
                    speed: parseInt(speed)
                }));
            }
            
            function stopMotor(motor) {
                if (!robotConnected) {
                    alert('Сначала подключитесь к роботу!');
                    return;
                }
                
                if (!websocket || websocket.readyState !== WebSocket.OPEN) {
                    alert('WebSocket не подключен');
                    return;
                }
                
                websocket.send(JSON.stringify({
                    command: 'stop_motor',
                    motor: motor
                }));
            }
            
            function updateSpeed(motor) {
                const speed = document.getElementById(`speed-${motor}`).value;
                document.getElementById(`speed-value-${motor}`).textContent = speed;
            }
            
            function setStartPosition(motor) {
                motorPositions[motor] = 0;
                document.getElementById(`motor-${motor}-position`).textContent = '0%';
                alert(`Стартовая позиция для мотора ${motor} установлена!`);
            }
            
            function measureForwardTime(motor) {
                if (!robotConnected) {
                    alert('Сначала подключитесь к роботу!');
                    return;
                }
                
                const startTime = Date.now();
                moveMotor(motor, 'forward', 255);
                
                // Очищаем предыдущий таймер если есть
                if (measurementTimers[`forward_${motor}`]) {
                    clearTimeout(measurementTimers[`forward_${motor}`]);
                }
                
                measurementTimers[`forward_${motor}`] = setTimeout(() => {
                    stopMotor(motor);
                    const endTime = Date.now();
                    const duration = (endTime - startTime) / 1000;
                    document.getElementById(`forward-time-${motor}`).textContent = duration.toFixed(2);
                    calibrationData[`${motor}_forward`] = duration;
                }, 5000); // 5 секунд максимум
            }
            
            function measureBackwardTime(motor) {
                if (!robotConnected) {
                    alert('Сначала подключитесь к роботу!');
                    return;
                }
                
                const startTime = Date.now();
                moveMotor(motor, 'backward', 255);
                
                // Очищаем предыдущий таймер если есть
                if (measurementTimers[`backward_${motor}`]) {
                    clearTimeout(measurementTimers[`backward_${motor}`]);
                }
                
                measurementTimers[`backward_${motor}`] = setTimeout(() => {
                    stopMotor(motor);
                    const endTime = Date.now();
                    const duration = (endTime - startTime) / 1000;
                    document.getElementById(`backward-time-${motor}`).textContent = duration.toFixed(2);
                    calibrationData[`${motor}_backward`] = duration;
                }, 5000); // 5 секунд максимум
            }
            
            function saveCalibration() {
                console.log('Сохранение калибровки:', calibrationData);
                alert('Калибровка сохранена! (пока через API)');
                // TODO: Реализовать сохранение через API
            }
            
            function saveStartPosition() {
                console.log('Сохранение стартовой позиции:', motorPositions);
                alert('Стартовая позиция сохранена! (пока через API)');
                // TODO: Реализовать сохранение через API
            }
            
            // Подключаемся к WebSocket при загрузке страницы
            window.addEventListener('load', function() {
                connectWebSocket();
            });
            
            // Очищаем таймеры при закрытии страницы
            window.addEventListener('beforeunload', function() {
                Object.values(measurementTimers).forEach(timer => clearTimeout(timer));
                if (websocket) {
                    websocket.close();
                }
            });
        </script>
    </body>
    </html>
    """

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
