#!/usr/bin/env python3
"""
Пример использования API-only системы калибровки и управления роботом
"""

import asyncio
import sys
import os

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_calibrate import EnhancedMotorCalibrator
from classes.calibrated_robot_arm import CalibratedRobotArm

async def main():
    """Основная функция"""
    print("🤖 ESP32 Robot Arm - API-Only System")
    print("=" * 50)
    
    robot_id = "esp32_robot_arm_001"
    server_url = "http://localhost:8000/api"
    
    # Проверяем доступность API
    calibrator = EnhancedMotorCalibrator(robot_id=robot_id, server_url=server_url)
    api_available = await calibrator.test_api_connection()
    
    if not api_available:
        print("❌ API server is not available!")
        print("Please start the server: cd python/server && python3 data_server.py")
        return
    
    print("✅ API server is running")
    
    # Выбор действия
    print("\nChoose action:")
    print("1. Calibrate robot (Enhanced)")
    print("2. Use calibrated robot")
    print("3. Test API connection")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        # Калибровка
        print("\n🔧 Starting Enhanced Calibration...")
        await calibrator.interactive_calibration()
        
    elif choice == "2":
        # Использование откалиброванного робота
        print("\n🎮 Using Calibrated Robot...")
        robot_arm = CalibratedRobotArm(robot_id=robot_id, server_url=server_url)
        
        # Подключение
        if await robot_arm.connect():
            print("✅ Connected to robot")
            
            # Показываем статус
            robot_arm.show_calibration_status()
            robot_arm.show_start_position_status()
            
            # Проверяем стартовую позицию
            await robot_arm.verify_start_position()
            
            # Простые команды
            print("\nSimple commands:")
            print("1. Move to home position")
            print("2. Move to ready position")
            print("3. Move to pick position")
            print("4. Move to place position")
            print("5. Move to rest position")
            
            cmd_choice = input("\nEnter command (1-5): ").strip()
            
            if cmd_choice == "1":
                await robot_arm.move_to_home()
            elif cmd_choice == "2":
                await robot_arm.move_to_ready()
            elif cmd_choice == "3":
                await robot_arm.move_to_pick()
            elif cmd_choice == "4":
                await robot_arm.move_to_place()
            elif cmd_choice == "5":
                await robot_arm.move_to_rest()
            
            # Отключение
            await robot_arm.disconnect()
            
        else:
            print("❌ Failed to connect to robot")
            
    elif choice == "3":
        # Тест API
        print("\n🔍 Testing API Connection...")
        await calibrator.test_api_connection()
        
    else:
        print("Invalid choice")

if __name__ == "__main__":
    asyncio.run(main())
