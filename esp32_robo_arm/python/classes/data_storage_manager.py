#!/usr/bin/env python3
"""
Robot Arm Data Storage Manager
Универсальный менеджер для хранения калибровочных данных и позиций
"""

import json
import os
import asyncio
import aiohttp
import sqlite3
from datetime import datetime
from typing import Dict, Optional, Any, List
from dataclasses import dataclass, asdict
from enum import Enum

class StorageType(Enum):
    """Типы хранения данных"""
    LOCAL_FILE = "local_file"
    SERVER_API = "server_api"
    DATABASE = "database"
    HYBRID = "hybrid"

@dataclass
class MotorCalibrationData:
    """Данные калибровки мотора"""
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

@dataclass
class RobotPosition:
    """Текущая позиция робота"""
    timestamp: str
    motor_positions: Dict[int, float]  # {motor_id: position_percentage}
    position_name: Optional[str] = None  # "home", "pick", etc.

@dataclass
class RobotState:
    """Полное состояние робота"""
    robot_id: str
    last_update: str
    calibration_data: Dict[int, MotorCalibrationData]
    current_position: RobotPosition
    is_connected: bool = False

class RobotDataStorage:
    """Универсальный менеджер хранения данных робота"""
    
    def __init__(self, 
                 robot_id: str = "esp32_robot_arm_001",
                 storage_type: StorageType = StorageType.HYBRID,
                 local_file_path: str = None,
                 server_url: str = None,
                 db_path: str = None):
        
        self.robot_id = robot_id
        self.storage_type = storage_type
        
        # Локальные пути
        if local_file_path is None:
            self.local_file_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "data", "robot_data.json"
            )
        else:
            self.local_file_path = local_file_path
            
        # Серверные настройки
        self.server_url = server_url or "http://localhost:8000/api"
        
        # База данных
        if db_path is None:
            self.db_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "data", "robot_data.db"
            )
        else:
            self.db_path = db_path
            
        # Создаем директории если не существуют
        os.makedirs(os.path.dirname(self.local_file_path), exist_ok=True)
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # Инициализация базы данных
        if storage_type in [StorageType.DATABASE, StorageType.HYBRID]:
            self._init_database()
    
    def _init_database(self):
        """Инициализация SQLite базы данных"""
        conn = sqlite3.connect(self.db_path)
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
                motor_positions TEXT NOT NULL,  -- JSON string
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
                current_position TEXT NOT NULL,  -- JSON string
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(robot_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    async def save_calibration_data(self, calibration_data: Dict[int, MotorCalibrationData]) -> bool:
        """Сохранение калибровочных данных"""
        try:
            if self.storage_type in [StorageType.LOCAL_FILE, StorageType.HYBRID]:
                await self._save_calibration_local(calibration_data)
            
            if self.storage_type in [StorageType.SERVER_API, StorageType.HYBRID]:
                await self._save_calibration_server(calibration_data)
            
            if self.storage_type in [StorageType.DATABASE, StorageType.HYBRID]:
                await self._save_calibration_database(calibration_data)
            
            return True
        except Exception as e:
            print(f"Error saving calibration data: {e}")
            return False
    
    async def load_calibration_data(self) -> Dict[int, MotorCalibrationData]:
        """Загрузка калибровочных данных"""
        try:
            if self.storage_type == StorageType.LOCAL_FILE:
                return await self._load_calibration_local()
            elif self.storage_type == StorageType.SERVER_API:
                return await self._load_calibration_server()
            elif self.storage_type == StorageType.DATABASE:
                return await self._load_calibration_database()
            elif self.storage_type == StorageType.HYBRID:
                # Пробуем загрузить с сервера, если не получается - с локального файла
                try:
                    return await self._load_calibration_server()
                except:
                    return await self._load_calibration_local()
        except Exception as e:
            print(f"Error loading calibration data: {e}")
            return {}
    
    async def save_current_position(self, position: RobotPosition) -> bool:
        """Сохранение текущей позиции"""
        try:
            if self.storage_type in [StorageType.LOCAL_FILE, StorageType.HYBRID]:
                await self._save_position_local(position)
            
            if self.storage_type in [StorageType.SERVER_API, StorageType.HYBRID]:
                await self._save_position_server(position)
            
            if self.storage_type in [StorageType.DATABASE, StorageType.HYBRID]:
                await self._save_position_database(position)
            
            return True
        except Exception as e:
            print(f"Error saving position: {e}")
            return False
    
    async def load_current_position(self) -> Optional[RobotPosition]:
        """Загрузка текущей позиции"""
        try:
            if self.storage_type == StorageType.LOCAL_FILE:
                return await self._load_position_local()
            elif self.storage_type == StorageType.SERVER_API:
                return await self._load_position_server()
            elif self.storage_type == StorageType.DATABASE:
                return await self._load_position_database()
            elif self.storage_type == StorageType.HYBRID:
                try:
                    return await self._load_position_server()
                except:
                    return await self._load_position_local()
        except Exception as e:
            print(f"Error loading position: {e}")
            return None
    
    # Локальные методы сохранения
    async def _save_calibration_local(self, calibration_data: Dict[int, MotorCalibrationData]):
        """Сохранение калибровочных данных в локальный файл"""
        data = {}
        for motor_id, calib_data in calibration_data.items():
            data[str(motor_id)] = asdict(calib_data)
        
        with open(self.local_file_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    async def _load_calibration_local(self) -> Dict[int, MotorCalibrationData]:
        """Загрузка калибровочных данных из локального файла"""
        if not os.path.exists(self.local_file_path):
            return {}
        
        with open(self.local_file_path, 'r') as f:
            data = json.load(f)
        
        calibration_data = {}
        for motor_id_str, calib_dict in data.items():
            motor_id = int(motor_id_str)
            calibration_data[motor_id] = MotorCalibrationData(**calib_dict)
        
        return calibration_data
    
    async def _save_position_local(self, position: RobotPosition):
        """Сохранение позиции в локальный файл"""
        position_file = self.local_file_path.replace('.json', '_position.json')
        with open(position_file, 'w') as f:
            json.dump(asdict(position), f, indent=2)
    
    async def _load_position_local(self) -> Optional[RobotPosition]:
        """Загрузка позиции из локального файла"""
        position_file = self.local_file_path.replace('.json', '_position.json')
        if not os.path.exists(position_file):
            return None
        
        with open(position_file, 'r') as f:
            data = json.load(f)
        
        return RobotPosition(**data)
    
    # Серверные методы
    async def _save_calibration_server(self, calibration_data: Dict[int, MotorCalibrationData]):
        """Сохранение калибровочных данных на сервер"""
        async with aiohttp.ClientSession() as session:
            data = {
                "robot_id": self.robot_id,
                "calibration_data": {str(k): asdict(v) for k, v in calibration_data.items()}
            }
            
            async with session.post(
                f"{self.server_url}/calibration",
                json=data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status != 200:
                    raise Exception(f"Server error: {response.status}")
    
    async def _load_calibration_server(self) -> Dict[int, MotorCalibrationData]:
        """Загрузка калибровочных данных с сервера"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.server_url}/calibration/{self.robot_id}") as response:
                if response.status != 200:
                    raise Exception(f"Server error: {response.status}")
                
                data = await response.json()
                calibration_data = {}
                
                for motor_id_str, calib_dict in data["calibration_data"].items():
                    motor_id = int(motor_id_str)
                    calibration_data[motor_id] = MotorCalibrationData(**calib_dict)
                
                return calibration_data
    
    async def _save_position_server(self, position: RobotPosition):
        """Сохранение позиции на сервер"""
        async with aiohttp.ClientSession() as session:
            data = {
                "robot_id": self.robot_id,
                "position": asdict(position)
            }
            
            async with session.post(
                f"{self.server_url}/position",
                json=data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status != 200:
                    raise Exception(f"Server error: {response.status}")
    
    async def _load_position_server(self) -> Optional[RobotPosition]:
        """Загрузка позиции с сервера"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.server_url}/position/{self.robot_id}") as response:
                if response.status == 404:
                    return None
                if response.status != 200:
                    raise Exception(f"Server error: {response.status}")
                
                data = await response.json()
                return RobotPosition(**data["position"])
    
    # Методы базы данных
    async def _save_calibration_database(self, calibration_data: Dict[int, MotorCalibrationData]):
        """Сохранение калибровочных данных в базу данных"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for motor_id, calib_data in calibration_data.items():
            cursor.execute('''
                INSERT OR REPLACE INTO motor_calibration 
                (robot_id, motor_id, calibrated, calibration_date, forward_time, 
                 backward_time, speed, min_position, max_position, return_time, 
                 total_travel_time, average_travel_time, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                self.robot_id, motor_id, calib_data.calibrated,
                calib_data.calibration_date, calib_data.forward_time,
                calib_data.backward_time, calib_data.speed,
                calib_data.min_position, calib_data.max_position,
                calib_data.return_time, calib_data.total_travel_time,
                calib_data.average_travel_time, datetime.now().isoformat()
            ))
        
        conn.commit()
        conn.close()
    
    async def _load_calibration_database(self) -> Dict[int, MotorCalibrationData]:
        """Загрузка калибровочных данных из базы данных"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT motor_id, calibrated, calibration_date, forward_time,
                   backward_time, speed, min_position, max_position,
                   return_time, total_travel_time, average_travel_time
            FROM motor_calibration 
            WHERE robot_id = ?
        ''', (self.robot_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        calibration_data = {}
        for row in rows:
            motor_id = row[0]
            calibration_data[motor_id] = MotorCalibrationData(
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
        
        return calibration_data
    
    async def _save_position_database(self, position: RobotPosition):
        """Сохранение позиции в базу данных"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Сохраняем историю позиций
        cursor.execute('''
            INSERT INTO robot_positions 
            (robot_id, timestamp, motor_positions, position_name)
            VALUES (?, ?, ?, ?)
        ''', (
            self.robot_id, position.timestamp,
            json.dumps(position.motor_positions), position.position_name
        ))
        
        # Обновляем текущее состояние
        cursor.execute('''
            INSERT OR REPLACE INTO robot_states 
            (robot_id, last_update, is_connected, current_position)
            VALUES (?, ?, ?, ?)
        ''', (
            self.robot_id, position.timestamp, True,
            json.dumps(asdict(position))
        ))
        
        conn.commit()
        conn.close()
    
    async def _load_position_database(self) -> Optional[RobotPosition]:
        """Загрузка позиции из базы данных"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT current_position FROM robot_states 
            WHERE robot_id = ?
        ''', (self.robot_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            data = json.loads(row[0])
            return RobotPosition(**data)
        
        return None
    
    async def get_position_history(self, limit: int = 100) -> List[RobotPosition]:
        """Получение истории позиций"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT timestamp, motor_positions, position_name
            FROM robot_positions 
            WHERE robot_id = ?
            ORDER BY created_at DESC
            LIMIT ?
        ''', (self.robot_id, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        positions = []
        for row in rows:
            positions.append(RobotPosition(
                timestamp=row[0],
                motor_positions=json.loads(row[1]),
                position_name=row[2]
            ))
        
        return positions
    
    async def sync_data(self) -> bool:
        """Синхронизация данных между всеми источниками"""
        try:
            if self.storage_type != StorageType.HYBRID:
                return True
            
            # Загружаем данные с сервера
            server_calibration = await self._load_calibration_server()
            server_position = await self._load_position_server()
            
            # Сохраняем локально
            if server_calibration:
                await self._save_calibration_local(server_calibration)
            if server_position:
                await self._save_position_local(server_position)
            
            return True
        except Exception as e:
            print(f"Sync error: {e}")
            return False

# Пример использования
async def main():
    """Пример использования системы хранения данных"""
    
    # Создаем менеджер хранения
    storage = RobotDataStorage(
        robot_id="esp32_robot_arm_001",
        storage_type=StorageType.HYBRID,
        server_url="http://localhost:8000/api"
    )
    
    # Пример калибровочных данных
    calibration_data = {
        0: MotorCalibrationData(
            motor_id=0,
            calibrated=True,
            calibration_date=datetime.now().isoformat(),
            forward_time=9.2,
            backward_time=14.4,
            speed=150
        ),
        1: MotorCalibrationData(
            motor_id=1,
            calibrated=True,
            calibration_date=datetime.now().isoformat(),
            forward_time=25.1,
            backward_time=43.4,
            speed=150
        )
    }
    
    # Сохраняем калибровочные данные
    await storage.save_calibration_data(calibration_data)
    
    # Пример текущей позиции
    current_position = RobotPosition(
        timestamp=datetime.now().isoformat(),
        motor_positions={0: 0.5, 1: 0.3, 2: 0.7},
        position_name="pick"
    )
    
    # Сохраняем позицию
    await storage.save_current_position(current_position)
    
    # Загружаем данные
    loaded_calibration = await storage.load_calibration_data()
    loaded_position = await storage.load_current_position()
    
    print("Calibration data loaded:", len(loaded_calibration), "motors")
    print("Current position loaded:", loaded_position)

if __name__ == "__main__":
    asyncio.run(main())
