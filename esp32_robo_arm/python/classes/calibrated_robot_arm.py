#!/usr/bin/env python3
"""
Calibrated Robot Arm Controller
Высокоуровневый контроллер робо-руки с использованием данных калибровки
"""

import asyncio
import json
import sys
import os
from typing import Dict, Optional, Tuple

# Добавляем родительскую папку в путь для импорта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from classes.robot_arm_controller import RobotArmController

class CalibratedRobotArm:
    """Высокоуровневый контроллер робо-руки с поддержкой калибровки"""
    
    def __init__(self, calibration_file: str = None):
        self.controller = RobotArmController()
        if calibration_file is None:
            self.calibration_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "motor_calibration", "motor_calibration.json")
        else:
            self.calibration_file = calibration_file
        self.calibration_data = {}
        self.connected = False
        
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
    
    async def connect(self):
        """Подключение к ESP32"""
        device = await self.controller.scan_for_device()
        if not device:
            print("Device not found! Make sure ESP32 is running and in range.")
            return False
            
        if await self.controller.connect(device):
            self.connected = True
            print("Connected to ESP32 Robot Arm")
            self.load_calibration_data()
            return True
        else:
            print("Failed to connect to device!")
            return False
    
    async def disconnect(self):
        """Отключение от ESP32"""
        if self.connected:
            await self.controller.disconnect()
            self.connected = False
            print("Disconnected from ESP32")
    
    def load_calibration_data(self):
        """Загрузка данных калибровки из файла"""
        if os.path.exists(self.calibration_file):
            try:
                with open(self.calibration_file, 'r') as f:
                    self.calibration_data = json.load(f)
                print(f"Loaded calibration data from {self.calibration_file}")
                return True
            except Exception as e:
                print(f"Error loading calibration data: {e}")
                return False
        else:
            print("No calibration file found. Calibrated movements will not be available.")
            return False
    
    def is_motor_calibrated(self, motor: int) -> bool:
        """Проверка, откалиброван ли мотор"""
        motor_key = str(motor)  # Конвертируем в строку для поиска в JSON
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
        """Получение времен движения для мотора
        
        Returns:
            Tuple[backward_time, return_time] - времена движения назад и возврата
        """
        if not self.is_motor_calibrated(motor):
            raise ValueError(f"Motor {motor} is not calibrated")
        
        motor_key = str(motor)  # Конвертируем в строку для поиска в JSON
        data = self.calibration_data[motor_key]
        return data["backward_time"], data["return_time"]
    
    async def move_to_percentage(self, motor: int, percentage: float, speed: int = 150):
        """Движение мотора на указанный процент от диапазона
        
        Args:
            motor: номер мотора (0, 1, 2)
            percentage: позиция от 0.0 (минимум) до 1.0 (максимум)
            speed: скорость движения (0-255)
        """
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
        
        return result
    
    async def move_to_position(self, position_name: str, speed: int = 150):
        """Движение в предустановленную позицию
        
        Args:
            position_name: название позиции (home, pick, place, rest, extended, retracted)
            speed: скорость движения (0-255)
        """
        if position_name not in self.POSITIONS:
            raise ValueError(f"Unknown position: {position_name}. Available: {list(self.POSITIONS.keys())}")
        
        position = self.POSITIONS[position_name]
        print(f"Moving to position: {position_name}")
        
        # Движем все моторы одновременно
        tasks = []
        for motor_key, percentage in position.items():
            motor_num = int(motor_key.split("_")[1])
            if self.is_motor_calibrated(motor_num):
                tasks.append(self.move_to_percentage(motor_num, percentage, speed))
            else:
                print(f"Warning: Motor {motor_num} is not calibrated, skipping")
        
        if tasks:
            await asyncio.gather(*tasks)
            
            # Обновляем текущие позиции после успешного движения
            for motor_key, percentage in position.items():
                motor_num = int(motor_key.split("_")[1])
                if self.is_motor_calibrated(motor_num):
                    self.current_positions[motor_num] = percentage
        else:
            print("No calibrated motors available for this position")
    
    async def smooth_move(self, motor: int, start_percentage: float, end_percentage: float, 
                         steps: int = 10, speed: int = 150, step_delay: float = 0.1):
        """Плавное движение между позициями
        
        Args:
            motor: номер мотора (0, 1, 2)
            start_percentage: начальная позиция (0.0-1.0)
            end_percentage: конечная позиция (0.0-1.0)
            steps: количество шагов для плавного движения
            speed: скорость движения (0-255)
            step_delay: задержка между шагами в секундах
        """
        if not self.connected:
            print("Not connected to device!")
            return False
        
        self.validate_percentage(motor, start_percentage)
        self.validate_percentage(motor, end_percentage)
        
        print(f"Smooth move: Motor {motor} from {start_percentage*100:.1f}% to {end_percentage*100:.1f}%")
        
        for i in range(steps):
            current_percentage = start_percentage + (end_percentage - start_percentage) * i / (steps - 1)
            await self.move_to_percentage(motor, current_percentage, speed)
            await asyncio.sleep(step_delay)
    
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
        await self.move_to_percentage(1, 0.9, speed)  # Поднять плечо
        await asyncio.sleep(1)
        
        # 4. Перемещение к месту размещения
        await self.move_to_position("place", speed)
        await asyncio.sleep(2)
        
        # 5. Опускание объекта
        await self.move_to_percentage(1, 0.3, speed)  # Опустить плечо
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
            await self.move_to_percentage(0, 0.2, speed)  # Влево
            await asyncio.sleep(0.5)
            await self.move_to_percentage(0, 0.8, speed)  # Вправо
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
                motor_key = str(motor)  # Конвертируем в строку для поиска в JSON
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
