#!/usr/bin/env python3
"""
Example: Calibration Start Position System
Пример использования системы стартовой позиции после калибровки
"""

import asyncio
import sys
import os

# Добавляем путь к классам
sys.path.append(os.path.join(os.path.dirname(__file__), 'classes'))

from enhanced_calibrate import EnhancedMotorCalibrator
from calibrated_robot_arm import CalibratedRobotArm

async def example_calibration_workflow():
    """Пример полного рабочего процесса с калибровкой и использованием"""
    
    print("🤖 ESP32 Robot Arm - Complete Calibration Workflow")
    print("=" * 60)
    
    # Шаг 1: Калибровка моторов
    print("\n1️⃣ STEP 1: Motor Calibration")
    print("-" * 30)
    
    calibrator = EnhancedMotorCalibrator(
        robot_id="esp32_robot_arm_001",
        server_url="http://localhost:8000/api",
        use_api=True,
        fallback_to_file=True
    )
    
    # Проверяем API
    api_available = await calibrator.test_api_connection()
    if not api_available:
        calibrator.use_api = False
        calibrator.fallback_to_file = True
        print("Using file-only mode")
    
    # Подключаемся к роботу
    print("Connecting to robot...")
    if await calibrator.connect():
        print("✅ Connected to robot!")
        
        # Загружаем существующие данные
        await calibrator.load_calibration_data()
        
        # Показываем статус калибровки
        calibrator.show_calibration_status()
        
        # Сохраняем стартовую позицию (имитируем завершение калибровки)
        print("\nSaving calibration start position...")
        await calibrator.save_calibration_start_position()
        
        await calibrator.disconnect()
        print("✅ Calibration workflow completed!")
    else:
        print("❌ Failed to connect to robot!")
        return
    
    # Шаг 2: Использование робота с загруженной стартовой позицией
    print("\n2️⃣ STEP 2: Using Robot with Start Position")
    print("-" * 40)
    
    robot = CalibratedRobotArm()
    
    # Подключаемся к роботу
    print("Connecting to robot...")
    if await robot.connect():
        print("✅ Connected to robot!")
        
        # Показываем статус стартовой позиции
        robot.show_start_position_status()
        
        # Проверяем, что робот в правильной позиции
        print("\nVerifying start position...")
        is_correct = await robot.verify_start_position()
        
        if is_correct:
            print("✅ Robot is in correct start position!")
            
            # Демонстрация движений
            print("\n3️⃣ STEP 3: Demonstration Movements")
            print("-" * 35)
            
            # Показываем доступные позиции
            robot.show_available_positions()
            
            # Движение в позицию "pick"
            print("\nMoving to PICK position...")
            await robot.move_to_position("pick")
            
            # Показываем текущие позиции
            robot.show_current_positions()
            
            # Движение в позицию "home"
            print("\nMoving to HOME position...")
            await robot.move_to_position("home")
            
            # Показываем финальные позиции
            robot.show_current_positions()
            
        else:
            print("⚠️  Robot is not in correct start position!")
            print("Consider recalibrating or manually moving to start position")
        
        await robot.disconnect()
        print("✅ Robot usage completed!")
    else:
        print("❌ Failed to connect to robot!")
    
    print("\n" + "=" * 60)
    print("🎉 COMPLETE WORKFLOW DEMONSTRATION FINISHED!")
    print("=" * 60)
    
    print("\nKey Benefits Demonstrated:")
    print("✅ Automatic start position saving after calibration")
    print("✅ Automatic start position loading on robot startup")
    print("✅ Position verification and validation")
    print("✅ Accurate movement calculations from known position")
    print("✅ Data persistence in file and API")
    print("✅ Seamless integration with existing code")

async def example_position_management():
    """Пример управления позициями"""
    
    print("\n🎯 Position Management Examples")
    print("=" * 40)
    
    robot = CalibratedRobotArm()
    
    # Подключаемся к роботу
    if await robot.connect():
        print("✅ Connected to robot!")
        
        # Загружаем стартовую позицию
        await robot.load_calibration_start_position()
        
        # Показываем статус
        robot.show_start_position_status()
        
        # Проверяем позицию
        is_correct = await robot.verify_start_position()
        
        if is_correct:
            print("✅ Robot is in correct start position!")
            
            # Демонстрация различных движений
            print("\nDemonstrating various movements...")
            
            # Плавное движение мотора 0
            print("\nSmooth movement of motor 0...")
            await robot.smooth_move(0, 0.0, 0.5, steps=5, step_delay=0.3)
            
            # Движение в предустановленную позицию
            print("\nMoving to REST position...")
            await robot.move_to_position("rest")
            
            # Возврат в стартовую позицию
            print("\nReturning to start position...")
            await robot.move_to_position("home")
            
            # Финальная проверка
            print("\nFinal position verification...")
            await robot.verify_start_position()
            
        else:
            print("⚠️  Robot position needs correction!")
        
        await robot.disconnect()
        print("✅ Position management demo completed!")

async def main():
    """Основная функция"""
    
    print("Choose demo:")
    print("1. Complete calibration workflow")
    print("2. Position management examples")
    print("3. Both demos")
    
    choice = input("Choose option (1-3): ").strip()
    
    if choice == "1":
        await example_calibration_workflow()
    elif choice == "2":
        await example_position_management()
    elif choice == "3":
        await example_calibration_workflow()
        await example_position_management()
    else:
        print("Invalid choice!")

if __name__ == "__main__":
    asyncio.run(main())
