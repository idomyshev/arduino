#!/usr/bin/env python3
"""
Motor Calibration Module
Модуль калибровки моторов робо-руки
"""

import asyncio
import json
import sys
import os
import time
from datetime import datetime

# Добавляем родительскую папку в путь для импорта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from classes.robot_arm_controller import RobotArmController

class MotorCalibrator:
    """Класс для калибровки моторов робо-руки"""
    
    def __init__(self):
        self.controller = RobotArmController()
        self.connected = False
        self.calibration_data = {}
        self.calibration_file = "motor_calibration.json"
        
    async def connect(self):
        """Подключение к ESP32"""
        device = await self.controller.scan_for_device()
        if not device:
            print("Device not found! Make sure ESP32 is running and in range.")
            return False
            
        if await self.controller.connect(device):
            self.connected = True
            print("Connected to ESP32 Robot Arm")
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
            print("No calibration file found. Starting fresh calibration.")
            return False
    
    def save_calibration_data(self):
        """Сохранение данных калибровки в файл"""
        try:
            with open(self.calibration_file, 'w') as f:
                json.dump(self.calibration_data, f, indent=2)
            print(f"Calibration data saved to {self.calibration_file}")
            return True
        except Exception as e:
            print(f"Error saving calibration data: {e}")
            return False
    
    async def calibrate_motor(self, motor):
        """Калибровка конкретного мотора
        
        Args:
            motor: номер мотора (0, 1, 2)
        """
        if not self.connected:
            print("Not connected to device!")
            return False
        
        print(f"\n{'='*60}")
        print(f"CALIBRATING MOTOR {motor}")
        print(f"{'='*60}")
        
        # Инициализируем данные калибровки для мотора
        if motor not in self.calibration_data:
            self.calibration_data[motor] = {
                "calibrated": False,
                "calibration_date": None,
                "forward_time": None,
                "backward_time": None,
                "speed": None,
                "positions": {
                    "min": None,
                    "max": None
                }
            }
        
        print(f"\nMotor {motor} calibration steps:")
        print("1. Move to MINIMUM position (forward direction)")
        print("2. Move to MAXIMUM position (backward direction)")
        print("3. Measure travel time")
        
        input("\nPress Enter to start calibration...")
        
        # Шаг 1: Движение к минимальному положению (вперед)
        print(f"\nStep 1: Moving motor {motor} to MINIMUM position...")
        print("Watch the robot arm and press Enter when it reaches the MINIMUM position")
        
        speed = 150  # Скорость калибровки
        start_time = time.time()
        
        # Запускаем мотор вперед
        await self.controller.send_command(motor, "forward", speed)
        
        # Ждем подтверждения от пользователя
        input("Press Enter when MINIMUM position is reached...")
        
        # Останавливаем мотор
        await self.controller.send_command(motor, "forward", 0)
        forward_time = time.time() - start_time
        
        print(f"✓ MINIMUM position reached in {forward_time:.2f} seconds")
        
        # Шаг 2: Движение к максимальному положению (назад)
        print(f"\nStep 2: Moving motor {motor} to MAXIMUM position...")
        print("Watch the robot arm and press Enter when it reaches the MAXIMUM position")
        
        input("Press Enter to start moving to MAXIMUM position...")
        
        start_time = time.time()
        
        # Запускаем мотор назад
        await self.controller.send_command(motor, "backward", speed)
        
        # Ждем подтверждения от пользователя
        input("Press Enter when MAXIMUM position is reached...")
        
        # Останавливаем мотор
        await self.controller.send_command(motor, "forward", 0)
        backward_time = time.time() - start_time
        
        print(f"✓ MAXIMUM position reached in {backward_time:.2f} seconds")
        
        # Шаг 3: Возврат в исходное положение
        print(f"\nStep 3: Returning motor {motor} to MINIMUM position...")
        print("This will measure the complete travel time")
        
        input("Press Enter to start return journey...")
        
        start_time = time.time()
        
        # Возвращаемся в минимальное положение
        await self.controller.send_command(motor, "forward", speed)
        
        # Ждем подтверждения от пользователя
        input("Press Enter when MINIMUM position is reached again...")
        
        # Останавливаем мотор
        await self.controller.send_command(motor, "forward", 0)
        return_time = time.time() - start_time
        
        print(f"✓ Return journey completed in {return_time:.2f} seconds")
        
        # Сохраняем данные калибровки
        self.calibration_data[motor].update({
            "calibrated": True,
            "calibration_date": datetime.now().isoformat(),
            "forward_time": forward_time,
            "backward_time": backward_time,
            "return_time": return_time,
            "speed": speed,
            "total_travel_time": forward_time + backward_time,
            "average_travel_time": (forward_time + backward_time) / 2
        })
        
        print(f"\n✓ Motor {motor} calibration completed!")
        print(f"  Forward time: {forward_time:.2f}s")
        print(f"  Backward time: {backward_time:.2f}s")
        print(f"  Return time: {return_time:.2f}s")
        print(f"  Average travel time: {self.calibration_data[motor]['average_travel_time']:.2f}s")
        
        return True
    
    def show_calibration_status(self):
        """Показать статус калибровки всех моторов"""
        print(f"\n{'='*50}")
        print("CALIBRATION STATUS")
        print(f"{'='*50}")
        
        for motor in range(3):
            if motor in self.calibration_data and self.calibration_data[motor]["calibrated"]:
                data = self.calibration_data[motor]
                print(f"Motor {motor}: ✓ CALIBRATED")
                print(f"  Date: {data['calibration_date']}")
                print(f"  Speed: {data['speed']}")
                print(f"  Forward time: {data['forward_time']:.2f}s")
                print(f"  Backward time: {data['backward_time']:.2f}s")
                print(f"  Average travel time: {data['average_travel_time']:.2f}s")
            else:
                print(f"Motor {motor}: ✗ NOT CALIBRATED")
            print()
    
    async def interactive_calibration(self):
        """Интерактивный режим калибровки"""
        print("=" * 60)
        print("MOTOR CALIBRATION MODE")
        print("=" * 60)
        
        if not await self.connect():
            return False
        
        # Загружаем существующие данные калибровки
        self.load_calibration_data()
        
        try:
            while True:
                print("\nAvailable commands:")
                print("  calibrate <motor>  - Calibrate specific motor (0, 1, 2)")
                print("  status             - Show calibration status")
                print("  save               - Save calibration data")
                print("  quit               - Exit calibration mode")
                
                command = input("\nCalibration> ").strip().lower()
                
                if command == "quit":
                    break
                elif command == "status":
                    self.show_calibration_status()
                elif command == "save":
                    self.save_calibration_data()
                elif command.startswith("calibrate "):
                    try:
                        motor = int(command.split()[1])
                        if motor < 0 or motor > 2:
                            print("Motor must be 0, 1, or 2")
                            continue
                        await self.calibrate_motor(motor)
                    except (ValueError, IndexError):
                        print("Usage: calibrate <motor> (0, 1, 2)")
                else:
                    print("Unknown command")
            
            # Сохраняем данные перед выходом
            self.save_calibration_data()
            return True
            
        except KeyboardInterrupt:
            print("\nCalibration interrupted by user")
            return False
        finally:
            await self.disconnect()

async def main():
    """Основная функция"""
    calibrator = MotorCalibrator()
    await calibrator.interactive_calibration()

if __name__ == "__main__":
    asyncio.run(main())
