#!/usr/bin/env python3
"""
Enhanced Calibrated Robot Arm Controller
Улучшенный контроллер робо-руки с поддержкой сохранения позиций
"""

import asyncio
import json
import sys
import os
from datetime import datetime
from typing import Dict, Optional, Tuple

# Добавляем родительскую папку в путь для импорта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from classes.robot_arm_controller import RobotArmController
from classes.data_storage_manager import RobotDataStorage, StorageType, MotorCalibrationData, RobotPosition

class EnhancedCalibratedRobotArm:
    """Улучшенный контроллер робо-руки с поддержкой сохранения позиций"""
    
    def __init__(self, 
                 robot_id: str = "esp32_robot_arm_001",
                 storage_type: StorageType = StorageType.HYBRID,
                 calibration_file: str = None,
                 server_url: str = None):
        
        self.controller = RobotArmController()
        self.robot_id = robot_id
        self.connected = False
        
        # Инициализация системы хранения данных
        self.storage = RobotDataStorage(
            robot_id=robot_id,
            storage_type=storage_type,
            server_url=server_url
        )
        
        # Совместимость со старым API
        if calibration_file is None:
            self.calibration_file = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                "motor_calibration", "motor_calibration.json"
            )
        else:
            self.calibration_file = calibration_file
        
        # Отслеживание текущих позиций моторов
        self.current_positions = {0: 0.0, 1: 0.0, 2: 0.0}
        
        # Предустановленные позиции робо-руки
        self.POSITIONS = {
            "home": {"motor_0": 0.0, "motor_1": 0.0, "motor_2": 0.0},
            "pick": {"motor_0": 0.3, "motor_1": 0.7, "motor_2": 0.5},
            "place": {"motor_0": 0.8, "motor_1": 0.4, "motor_2": 0.2},
            "rest": {"motor_0": 0.1, "motor_1": 0.1, "motor_2": 0.1},
            "extended": {"motor_0": 1.0, "motor_1": 1.0, "motor_2": 1.0},
            "retracted": {"motor_0": 0.0, "motor_1": 0.0, "motor_2": 0.0}
        }
        
        # Данные калибровки (для совместимости)
        self.calibration_data = {}
    
    async def connect(self):
        """Подключение к ESP32 с загрузкой сохраненных данных"""
        device = await self.controller.scan_for_device()
        if not device:
            print("Device not found! Make sure ESP32 is running and in range.")
            return False
            
        if await self.controller.connect(device):
            self.connected = True
            print("Connected to ESP32 Robot Arm")
            
            # Загружаем данные из новой системы хранения
            await self.load_calibration_data()
            
            # Загружаем сохраненную позицию
            await self.load_saved_position()
            
            return True
        else:
            print("Failed to connect to device!")
            return False
    
    async def disconnect(self):
        """Отключение от ESP32 с сохранением текущей позиции"""
        if self.connected:
            # Сохраняем текущую позицию перед отключением
            await self.save_current_position("disconnect")
            
            await self.controller.disconnect()
            self.connected = False
            print("Disconnected from ESP32")
    
    async def load_calibration_data(self):
        """Загрузка данных калибровки из новой системы хранения"""
        try:
            # Загружаем из новой системы
            calibration_data = await self.storage.load_calibration_data()
            
            if calibration_data:
                # Конвертируем в старый формат для совместимости
                self.calibration_data = {}
                for motor_id, calib_data in calibration_data.items():
                    self.calibration_data[str(motor_id)] = {
                        "calibrated": calib_data.calibrated,
                        "calibration_date": calib_data.calibration_date,
                        "forward_time": calib_data.forward_time,
                        "backward_time": calib_data.backward_time,
                        "speed": calib_data.speed,
                        "positions": {
                            "min": calib_data.min_position,
                            "max": calib_data.max_position
                        },
                        "return_time": calib_data.return_time,
                        "total_travel_time": calib_data.total_travel_time,
                        "average_travel_time": calib_data.average_travel_time
                    }
                print(f"Loaded calibration data from storage system")
                return True
            else:
                # Пробуем загрузить из старого файла
                return self.load_calibration_data_legacy()
        except Exception as e:
            print(f"Error loading calibration data: {e}")
            return self.load_calibration_data_legacy()
    
    def load_calibration_data_legacy(self):
        """Загрузка данных калибровки из старого файла (для совместимости)"""
        if os.path.exists(self.calibration_file):
            try:
                with open(self.calibration_file, 'r') as f:
                    self.calibration_data = json.load(f)
                print(f"Loaded calibration data from legacy file: {self.calibration_file}")
                return True
            except Exception as e:
                print(f"Error loading legacy calibration data: {e}")
                return False
        else:
            print("No calibration file found. Calibrated movements will not be available.")
            return False
    
    async def load_saved_position(self):
        """Загрузка сохраненной позиции"""
        try:
            saved_position = await self.storage.load_current_position()
            if saved_position:
                # Обновляем текущие позиции
                for motor_id, position in saved_position.motor_positions.items():
                    if motor_id in self.current_positions:
                        self.current_positions[motor_id] = position
                
                print(f"Loaded saved position: {saved_position.position_name or 'custom'}")
                print(f"Motor positions: {self.current_positions}")
                return True
            else:
                print("No saved position found, starting from 0%")
                return False
        except Exception as e:
            print(f"Error loading saved position: {e}")
            return False
    
    async def save_current_position(self, position_name: str = None):
        """Сохранение текущей позиции"""
        try:
            current_position = RobotPosition(
                timestamp=datetime.now().isoformat(),
                motor_positions=self.current_positions.copy(),
                position_name=position_name
            )
            
            success = await self.storage.save_current_position(current_position)
            if success:
                print(f"Position saved: {position_name or 'custom'}")
            return success
        except Exception as e:
            print(f"Error saving position: {e}")
            return False
    
    def is_motor_calibrated(self, motor: int) -> bool:
        """Проверка, откалиброван ли мотор"""
        motor_key = str(motor)
        return (motor_key in self.calibration_data and 
                self.calibration_data[motor_key].get("calibrated", False))
    
    def validate_percentage(self, motor: int, percentage: float) -> bool:
        """Проверка корректности процентного значения"""
        if percentage < 0 or percentage > 1:
            raise ValueError(f"Position {percentage} is out of range [0, 1]")
        
        if not self.is_motor_calibrated(motor):
            raise ValueError(f"Motor {motor} is not calibrated")
        
        return True
    
    def reset_positions(self):
        """Сбросить отслеживание позиций моторов"""
        self.current_positions = {0: 0.0, 1: 0.0, 2: 0.0}
        print("Motor positions tracking reset to 0%")
    
    def get_current_position(self, motor: int) -> float:
        """Получить текущую позицию мотора"""
        return self.current_positions.get(motor, 0.0)
    
    def get_motor_times(self, motor: int) -> Tuple[float, float]:
        """Получение времен движения для мотора"""
        if not self.is_motor_calibrated(motor):
            raise ValueError(f"Motor {motor} is not calibrated")
        
        motor_key = str(motor)
        data = self.calibration_data[motor_key]
        return data["backward_time"], data["return_time"]
    
    async def move_to_percentage(self, motor: int, percentage: float, speed: int = 150, save_position: bool = True):
        """Движение мотора на указанный процент от диапазона"""
        if not self.connected:
            print("Not connected to device!")
            return False
        
        self.validate_percentage(motor, percentage)
        
        # Проверяем, не находимся ли мы уже в целевой позиции
        current_pos = self.current_positions[motor]
        position_tolerance = 0.02  # 2% толерантность
        if abs(percentage - current_pos) <= position_tolerance:
            print(f"Motor {motor} already at position {percentage*100:.1f}%")
            return True
        
        backward_time, return_time = self.get_motor_times(motor)
        
        # Вычисляем время движения от текущей позиции к целевой
        if percentage > current_pos:
            # Движение к максимальной позиции (backward)
            distance = percentage - current_pos
            target_time = int(backward_time * distance * 1000)  # в миллисекундах
            direction = "backward"
        else:
            # Движение к минимальной позиции (forward)
            distance = current_pos - percentage
            target_time = int(return_time * distance * 1000)  # в миллисекундах
            direction = "forward"
        
        print(f"Motor {motor} moving from {current_pos*100:.1f}% to {percentage*100:.1f}% ({direction}, {target_time}ms)")
        
        result = await self.controller.send_command(motor, direction, speed, target_time)
        
        # Обновляем текущую позицию
        if result:
            self.current_positions[motor] = percentage
            
            # Сохраняем позицию если требуется
            if save_position:
                await self.save_current_position()
        
        return result
    
    async def move_to_position(self, position_name: str, speed: int = 150, save_position: bool = True):
        """Движение в предустановленную позицию"""
        if position_name not in self.POSITIONS:
            raise ValueError(f"Unknown position: {position_name}. Available: {list(self.POSITIONS.keys())}")
        
        position = self.POSITIONS[position_name]
        print(f"Moving to position: {position_name}")
        
        # Движем все моторы одновременно
        tasks = []
        for motor_key, percentage in position.items():
            motor_num = int(motor_key.split("_")[1])
            if self.is_motor_calibrated(motor_num):
                tasks.append(self.move_to_percentage(motor_num, percentage, speed, save_position=False))
            else:
                print(f"Warning: Motor {motor_num} is not calibrated, skipping")
        
        if tasks:
            await asyncio.gather(*tasks)
            
            # Обновляем текущие позиции после успешного движения
            for motor_key, percentage in position.items():
                motor_num = int(motor_key.split("_")[1])
                if self.is_motor_calibrated(motor_num):
                    self.current_positions[motor_num] = percentage
            
            # Сохраняем позицию если требуется
            if save_position:
                await self.save_current_position(position_name)
        else:
            print("No calibrated motors available for this position")
    
    async def smooth_move(self, motor: int, start_percentage: float, end_percentage: float, 
                         steps: int = 10, speed: int = 150, step_delay: float = 0.1):
        """Плавное движение между позициями"""
        if not self.connected:
            print("Not connected to device!")
            return False
        
        self.validate_percentage(motor, start_percentage)
        self.validate_percentage(motor, end_percentage)
        
        print(f"Smooth move: Motor {motor} from {start_percentage*100:.1f}% to {end_percentage*100:.1f}%")
        
        for i in range(steps):
            current_percentage = start_percentage + (end_percentage - start_percentage) * i / (steps - 1)
            await self.move_to_percentage(motor, current_percentage, speed, save_position=False)
            await asyncio.sleep(step_delay)
        
        # Сохраняем финальную позицию
        await self.save_current_position("smooth_move")
    
    async def pick_and_place_sequence(self, speed: int = 150):
        """Демонстрационная последовательность: взять → переместить → положить"""
        print("Starting pick and place sequence...")
        
        # 1. Переход в позицию "home"
        await self.move_to_position("home", speed)
        await asyncio.sleep(1)
        
        # 2. Переход к объекту
        await self.move_to_position("pick", speed)
        await asyncio.sleep(2)
        
        # 3. Подъем объекта (имитация захвата)
        await self.move_to_percentage(1, 0.9, speed)
        await asyncio.sleep(1)
        
        # 4. Перемещение к месту размещения
        await self.move_to_position("place", speed)
        await asyncio.sleep(2)
        
        # 5. Опускание объекта
        await self.move_to_percentage(1, 0.3, speed)
        await asyncio.sleep(1)
        
        # 6. Возврат в исходное положение
        await self.move_to_position("home", speed)
        
        print("Pick and place sequence completed!")
    
    async def wave_sequence(self, speed: int = 150):
        """Демонстрационная последовательность: махание рукой"""
        print("Starting wave sequence...")
        
        # Переход в исходное положение
        await self.move_to_position("rest", speed)
        await asyncio.sleep(1)
        
        # Махание влево-вправо
        for _ in range(3):
            await self.move_to_percentage(0, 0.2, speed)
            await asyncio.sleep(0.5)
            await self.move_to_percentage(0, 0.8, speed)
            await asyncio.sleep(0.5)
        
        # Возврат в исходное положение
        await self.move_to_position("rest", speed)
        
        print("Wave sequence completed!")
    
    def show_calibration_status(self):
        """Показать статус калибровки всех моторов"""
        print(f"\n{'='*50}")
        print("CALIBRATION STATUS")
        print(f"{'='*50}")
        
        for motor in range(3):
            if self.is_motor_calibrated(motor):
                motor_key = str(motor)
                data = self.calibration_data[motor_key]
                print(f"Motor {motor}: ✓ CALIBRATED")
                print(f"  Date: {data['calibration_date']}")
                print(f"  Speed: {data['speed']}")
                print(f"  Min→Max time: {data['backward_time']:.2f}s")
                print(f"  Max→Min time: {data['return_time']:.2f}s")
            else:
                print(f"Motor {motor}: ✗ NOT CALIBRATED")
            print()
    
    def show_current_positions(self):
        """Показать текущие позиции всех моторов"""
        print(f"\n{'='*50}")
        print("CURRENT MOTOR POSITIONS")
        print(f"{'='*50}")
        
        for motor in range(3):
            if self.is_motor_calibrated(motor):
                position = self.current_positions[motor]
                print(f"Motor {motor}: {position*100:.1f}%")
            else:
                print(f"Motor {motor}: NOT CALIBRATED")
        print()
    
    def show_available_positions(self):
        """Показать доступные предустановленные позиции"""
        print(f"\n{'='*50}")
        print("AVAILABLE POSITIONS")
        print(f"{'='*50}")
        
        for name, position in self.POSITIONS.items():
            print(f"{name}:")
            for motor_key, percentage in position.items():
                motor_num = int(motor_key.split("_")[1])
                status = "✓" if self.is_motor_calibrated(motor_num) else "✗"
                print(f"  Motor {motor_num}: {percentage*100:.0f}% {status}")
            print()
    
    async def get_position_history(self, limit: int = 100):
        """Получение истории позиций"""
        try:
            return await self.storage.get_position_history(limit)
        except Exception as e:
            print(f"Error getting position history: {e}")
            return []
    
    async def sync_data(self):
        """Синхронизация данных с сервером"""
        try:
            return await self.storage.sync_data()
        except Exception as e:
            print(f"Error syncing data: {e}")
            return False

# Пример использования
async def main():
    """Пример использования улучшенного контроллера"""
    
    # Создаем контроллер с гибридным хранением
    robot = EnhancedCalibratedRobotArm(
        robot_id="esp32_robot_arm_001",
        storage_type=StorageType.HYBRID,
        server_url="http://localhost:8000/api"
    )
    
    # Подключаемся к роботу
    if await robot.connect():
        # Показываем статус
        robot.show_calibration_status()
        robot.show_current_positions()
        
        # Демонстрация движений
        await robot.move_to_position("home")
        await asyncio.sleep(2)
        
        await robot.move_to_position("pick")
        await asyncio.sleep(2)
        
        await robot.move_to_position("home")
        
        # Отключаемся
        await robot.disconnect()
    else:
        print("Failed to connect to robot")

if __name__ == "__main__":
    asyncio.run(main())
