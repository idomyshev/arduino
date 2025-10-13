#!/usr/bin/env python3
"""
Тестовый скрипт для проверки функциональности duration
"""

import asyncio
import json
import sys
import os

# Добавляем родительскую папку в путь для импорта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from classes.robot_arm_controller import RobotArmController

async def test_duration_functionality():
    """Тест новой функциональности duration"""
    print("Testing duration functionality...")
    
    controller = RobotArmController()
    
    try:
        # Поиск устройства
        device = await controller.scan_for_device()
        if not device:
            print("Device not found! Make sure ESP32 is running and in range.")
            return False
            
        # Подключение
        if not await controller.connect(device):
            print("Failed to connect to device!")
            return False
            
        print("Connected successfully!")
        
        # Тест 1: Команда без duration (должна работать бесконечно)
        print("\nTest 1: Command without duration (should run indefinitely)")
        await controller.send_command(0, "forward", 100)
        await asyncio.sleep(1)
        
        # Тест 2: Команда с duration (должна остановиться автоматически)
        print("\nTest 2: Command with duration (should stop automatically after 2 seconds)")
        await controller.send_command(0, "backward", 150, duration=2000)
        await asyncio.sleep(3)  # Ждем больше времени работы
        
        # Тест 3: Несколько моторов с разным временем
        print("\nTest 3: Multiple motors with different durations")
        await controller.send_command(0, "forward", 120, duration=1500)  # 1.5 сек
        await controller.send_command(1, "backward", 120, duration=2500)  # 2.5 сек
        await controller.send_command(2, "forward", 120, duration=1000)   # 1 сек
        await asyncio.sleep(3)  # Ждем завершения всех движений
        
        # Тест 4: Остановка всех моторов
        print("\nTest 4: Stopping all motors")
        await controller.stop_all_motors()
        await asyncio.sleep(1)
        
        print("\nAll tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"Test failed with error: {e}")
        return False
    finally:
        await controller.disconnect()

if __name__ == "__main__":
    print("Duration Functionality Test")
    print("=" * 40)
    asyncio.run(test_duration_functionality())
