#!/usr/bin/env python3
"""
Enhanced Motor Calibration with API Storage
Улучшенная калибровка моторов с сохранением через API
"""

import asyncio
import json
import sys
import os
import time
import aiohttp
from datetime import datetime
from typing import Dict, Optional
from dataclasses import asdict

# Добавляем родительскую папку в путь для импорта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from classes.robot_arm_controller import RobotArmController
from classes.data_storage_manager import MotorCalibrationData

class EnhancedMotorCalibrator:
    """Улучшенный класс калибровки моторов с поддержкой API"""
    
    def __init__(self, 
                 robot_id: str = "esp32_robot_arm_001",
                 server_url: str = "http://localhost:8000/api"):
        
        self.controller = RobotArmController()
        self.connected = False
        self.calibration_data = {}
        self.robot_id = robot_id
        self.server_url = server_url
    
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
    
    async def load_calibration_data(self):
        """Загрузка данных калибровки из API"""
        try:
            await self._load_from_api()
            return True
        except Exception as e:
            print(f"Failed to load from API: {e}")
            print("Make sure API server is running: cd python/server && python3 data_server.py")
            return False
    
    async def _load_from_api(self):
        """Загрузка данных калибровки с сервера"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.server_url}/calibration/{self.robot_id}") as response:
                if response.status == 404:
                    print("No calibration data found on server")
                    return
                elif response.status != 200:
                    raise Exception(f"Server error: {response.status}")
                
                data = await response.json()
                calibration_data = {}
                
                for motor_id_str, calib_dict in data["calibration_data"].items():
                    motor_id = int(motor_id_str)
                    calibration_data[motor_id] = {
                        "calibrated": calib_dict["calibrated"],
                        "calibration_date": calib_dict["calibration_date"],
                        "forward_time": calib_dict["forward_time"],
                        "backward_time": calib_dict["backward_time"],
                        "speed": calib_dict["speed"],
                        "positions": {
                            "min": calib_dict.get("min_position"),
                            "max": calib_dict.get("max_position")
                        },
                        "return_time": calib_dict.get("return_time"),
                        "total_travel_time": calib_dict.get("total_travel_time"),
                        "average_travel_time": calib_dict.get("average_travel_time")
                    }
                
                self.calibration_data = calibration_data
                print(f"Loaded calibration data from API for robot {self.robot_id}")
    
    
    async def save_calibration_data(self):
        """Сохранение данных калибровки в API"""
        try:
            await self._save_to_api()
            print("✅ Calibration data saved to API")
            return True
        except Exception as e:
            print(f"❌ Failed to save to API: {e}")
            print("Make sure API server is running: cd python/server && python3 data_server.py")
            return False
    
    async def _save_to_api(self):
        """Сохранение данных калибровки на сервер"""
        # Конвертируем в формат API
        api_data = {}
        for motor_id, data in self.calibration_data.items():
            api_data[str(motor_id)] = MotorCalibrationData(
                motor_id=motor_id,
                calibrated=data["calibrated"],
                calibration_date=data["calibration_date"],
                forward_time=data["forward_time"],
                backward_time=data["backward_time"],
                speed=data["speed"],
                min_position=data["positions"]["min"],
                max_position=data["positions"]["max"],
                return_time=data.get("return_time"),
                total_travel_time=data.get("total_travel_time"),
                average_travel_time=data.get("average_travel_time")
            )
        
        async with aiohttp.ClientSession() as session:
            payload = {
                "robot_id": self.robot_id,
                "calibration_data": {str(k): asdict(data) for k, data in api_data.items()}
            }
            
            async with session.post(
                f"{self.server_url}/calibration",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status != 200:
                    raise Exception(f"Server error: {response.status}")
    
    
    async def calibrate_motor(self, motor: int, speed: int = 150):
        """Калибровка конкретного мотора
        
        Args:
            motor: номер мотора (0, 1, 2)
            speed: скорость калибровки (0-255)
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
                "speed": speed,
                "positions": {
                    "min": None,
                    "max": None
                },
                "return_time": None,
                "total_travel_time": None,
                "average_travel_time": None
            }
        
        print(f"Motor {motor} calibration started...")
        print(f"Speed: {speed}")
        print("\nInstructions:")
        print("1. Make sure the motor can move freely")
        print("2. The motor will move to MINIMUM position (forward)")
        print("3. Then move to MAXIMUM position (backward)")
        print("4. Finally return to MINIMUM position")
        print("\nPress ENTER when ready to start...")
        input()
        
        try:
            # 1. Движение к минимальной позиции (forward)
            print(f"\nStep 1: Moving motor {motor} to MINIMUM position (forward)...")
            print("Press ENTER when motor reaches minimum position...")
            
            start_time = time.time()
            await self.controller.send_command(motor, "forward", speed)
            input()
            forward_time = time.time() - start_time
            
            print(f"Forward time: {forward_time:.2f} seconds")
            
            # 2. Движение к максимальной позиции (backward)
            print(f"\nStep 2: Moving motor {motor} to MAXIMUM position (backward)...")
            print("Press ENTER when motor reaches maximum position...")
            
            start_time = time.time()
            await self.controller.send_command(motor, "backward", speed)
            input()
            backward_time = time.time() - start_time
            
            print(f"Backward time: {backward_time:.2f} seconds")
            
            # 3. Возврат к минимальной позиции (return)
            print(f"\nStep 3: Returning motor {motor} to MINIMUM position...")
            print("Press ENTER when motor reaches minimum position...")
            
            start_time = time.time()
            await self.controller.send_command(motor, "forward", speed)
            input()
            return_time = time.time() - start_time
            
            print(f"Return time: {return_time:.2f} seconds")
            
            # Сохраняем результаты калибровки
            self.calibration_data[motor].update({
                "calibrated": True,
                "calibration_date": datetime.now().isoformat(),
                "forward_time": forward_time,
                "backward_time": backward_time,
                "speed": speed,
                "return_time": return_time,
                "total_travel_time": forward_time + backward_time,
                "average_travel_time": (forward_time + backward_time) / 2
            })
            
            print(f"\n✅ Motor {motor} calibration completed!")
            print(f"   Forward time: {forward_time:.2f}s")
            print(f"   Backward time: {backward_time:.2f}s")
            print(f"   Return time: {return_time:.2f}s")
            print(f"   Total travel time: {forward_time + backward_time:.2f}s")
            
            return True
            
        except Exception as e:
            print(f"❌ Calibration failed: {e}")
            return False
    
    async def calibrate_all_motors(self, speed: int = 150):
        """Калибровка всех моторов"""
        print(f"\n{'='*60}")
        print("CALIBRATING ALL MOTORS")
        print(f"{'='*60}")
        
        for motor in range(3):
            success = await self.calibrate_motor(motor, speed)
            if not success:
                print(f"❌ Failed to calibrate motor {motor}")
                return False
            
            # Небольшая пауза между калибровками
            if motor < 2:
                print("\nPress ENTER to continue to next motor...")
                input()
        
        print(f"\n🎉 All motors calibrated successfully!")
        
        # Сохраняем стартовую позицию после калибровки всех моторов
        await self.save_calibration_start_position()
        
        return True
    
    async def interactive_calibration(self):
        """Интерактивная калибровка с API хранением"""
        print("ESP32 Robot Arm - Enhanced Motor Calibration (API Only)")
        print("=" * 60)
        
        # Выбор робота
        print(f"\nCurrent robot ID: {self.robot_id}")
        change_robot = input("Change robot ID? (y/n): ").lower().strip()
        if change_robot == 'y':
            self.robot_id = input("Enter robot ID: ").strip() or self.robot_id
        
        # Проверяем API
        print(f"\nChecking API server...")
        api_available = await self.test_api_connection()
        
        if not api_available:
            print("❌ API server is not available!")
            print("Please start the server: cd python/server && python3 data_server.py")
            return
        
        print("✅ Using API storage")
        
        # Подключение к роботу
        if not await self.connect():
            return
        
        try:
            # Загрузка существующих данных
            await self.load_calibration_data()
            
            # Показ текущего статуса калибровки
            self.show_calibration_status()
            
            # Выбор режима калибровки
            print(f"\nCalibration options:")
            print("1. Calibrate all motors")
            print("2. Calibrate specific motor")
            print("3. Recalibrate existing motor")
            
            choice = input("Choose option (1-3): ").strip()
            
            if choice == "1":
                speed = int(input("Enter calibration speed (0-255, default 150): ") or "150")
                await self.calibrate_all_motors(speed)
            elif choice == "2":
                motor = int(input("Enter motor number (0-2): "))
                speed = int(input("Enter calibration speed (0-255, default 150): ") or "150")
                await self.calibrate_motor(motor, speed)
            elif choice == "3":
                self.show_calibration_status()
                motor = int(input("Enter motor number to recalibrate (0-2): "))
                speed = int(input("Enter calibration speed (0-255, default 150): ") or "150")
                await self.calibrate_motor(motor, speed)
            else:
                print("Invalid choice!")
                return
            
            # Сохранение результатов
            print(f"\nSaving calibration data...")
            success = await self.save_calibration_data()
            
            if success:
                print("🎉 Calibration completed and saved successfully!")
                
                # Сохраняем стартовую позицию после калибровки
                print("Saving calibration start position...")
                await self.save_calibration_start_position()
            else:
                print("⚠️  Calibration completed but saving failed!")
            
            # Показ финального статуса
            self.show_calibration_status()
            
        finally:
            await self.disconnect()
    
    def show_calibration_status(self):
        """Показать статус калибровки всех моторов"""
        print(f"\n{'='*50}")
        print("CALIBRATION STATUS")
        print(f"{'='*50}")
        
        for motor in range(3):
            if motor in self.calibration_data and self.calibration_data[motor]["calibrated"]:
                data = self.calibration_data[motor]
                print(f"Motor {motor}: ✅ CALIBRATED")
                print(f"  Date: {data['calibration_date']}")
                print(f"  Speed: {data['speed']}")
                print(f"  Forward time: {data['forward_time']:.2f}s")
                print(f"  Backward time: {data['backward_time']:.2f}s")
                print(f"  Return time: {data['return_time']:.2f}s")
            else:
                print(f"Motor {motor}: ❌ NOT CALIBRATED")
            print()
    
    async def test_api_connection(self):
        """Тест подключения к API"""
        print("Testing API connection...")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.server_url}/status") as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"✅ API connection successful!")
                        print(f"   Server: {data['status']}")
                        print(f"   Version: {data['version']}")
                        print(f"   Database: {data['database']}")
                        return True
                    else:
                        print(f"❌ API error: {response.status}")
                        return False
        except Exception as e:
            print(f"❌ API connection failed: {e}")
            return False
    
    async def save_calibration_start_position(self):
        """Сохранение стартовой позиции после калибровки"""
        try:
            # После калибровки все моторы находятся в позиции 0% (минимальная)
            start_position = {
                0: 0.0,  # Мотор 0 в минимальной позиции
                1: 0.0,  # Мотор 1 в минимальной позиции  
                2: 0.0   # Мотор 2 в минимальной позиции
            }
            
            # Создаем объект позиции
            from classes.data_storage_manager import RobotPosition
            position = RobotPosition(
                timestamp=datetime.now().isoformat(),
                motor_positions=start_position,
                position_name="calibration_start"
            )
            
            # Сохраняем через API
            await self._save_position_to_api(position)
                
            print("✅ Calibration start position saved (all motors at 0%)")
            return True
            
        except Exception as e:
            print(f"❌ Failed to save calibration start position: {e}")
            return False
    
    async def _save_position_to_api(self, position):
        """Сохранение позиции на сервер"""
        async with aiohttp.ClientSession() as session:
            payload = {
                "robot_id": self.robot_id,
                "position": asdict(position)
            }
            
            async with session.post(
                f"{self.server_url}/position",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status != 200:
                    raise Exception(f"Server error: {response.status}")
    

# Пример использования
async def main():
    """Основная функция"""
    calibrator = EnhancedMotorCalibrator(
        robot_id="esp32_robot_arm_001",
        server_url="http://localhost:8000/api",
        use_api=True,
        fallback_to_file=True
    )
    
    # Тест подключения к API
    await calibrator.test_api_connection()
    
    # Запуск интерактивной калибровки
    await calibrator.interactive_calibration()

if __name__ == "__main__":
    asyncio.run(main())
