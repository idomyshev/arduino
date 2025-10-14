#!/usr/bin/env python3
"""
Quick Calibration Launcher
Быстрый запуск калибровки с API
"""

import asyncio
import sys
import os

# Добавляем путь к классам
sys.path.append(os.path.join(os.path.dirname(__file__), 'classes'))

from enhanced_calibrate import EnhancedMotorCalibrator

async def quick_calibration():
    """Быстрая калибровка с настройками по умолчанию"""
    
    print("🚀 ESP32 Robot Arm - Quick Calibration")
    print("=" * 50)
    
    # Проверяем, запущен ли сервер
    calibrator = EnhancedMotorCalibrator()
    
    print("Checking API server...")
    api_available = await calibrator.test_api_connection()
    
    if not api_available:
        print("\n⚠️  API server is not available!")
        print("Options:")
        print("1. Start server: cd python/server && python3 data_server.py")
        print("2. Use file-only mode")
        
        choice = input("\nUse file-only mode? (y/n): ").lower().strip()
        if choice == 'y':
            calibrator.use_api = False
            calibrator.fallback_to_file = True
            print("✅ Using file-only mode")
        else:
            print("Please start the server first!")
            return
    
    # Запуск калибровки
    await calibrator.interactive_calibration()

async def calibrate_single_motor():
    """Калибровка одного мотора"""
    
    print("🎯 Single Motor Calibration")
    print("=" * 30)
    
    calibrator = EnhancedMotorCalibrator()
    
    # Проверка API
    api_available = await calibrator.test_api_connection()
    if not api_available:
        calibrator.use_api = False
        calibrator.fallback_to_file = True
        print("Using file-only mode")
    
    # Подключение
    if not await calibrator.connect():
        return
    
    try:
        # Загрузка данных
        await calibrator.load_calibration_data()
        
        # Выбор мотора
        calibrator.show_calibration_status()
        motor = int(input("Enter motor number (0-2): "))
        speed = int(input("Enter speed (0-255, default 150): ") or "150")
        
        # Калибровка
        success = await calibrator.calibrate_motor(motor, speed)
        
        if success:
            # Сохранение
            await calibrator.save_calibration_data()
            print("✅ Calibration completed!")
        
    finally:
        await calibrator.disconnect()

async def calibrate_all_motors():
    """Калибровка всех моторов"""
    
    print("🔄 All Motors Calibration")
    print("=" * 30)
    
    calibrator = EnhancedMotorCalibrator()
    
    # Проверка API
    api_available = await calibrator.test_api_connection()
    if not api_available:
        calibrator.use_api = False
        calibrator.fallback_to_file = True
        print("Using file-only mode")
    
    # Подключение
    if not await calibrator.connect():
        return
    
    try:
        # Загрузка данных
        await calibrator.load_calibration_data()
        
        # Настройки
        speed = int(input("Enter calibration speed (0-255, default 150): ") or "150")
        
        # Калибровка всех моторов
        success = await calibrator.calibrate_all_motors(speed)
        
        if success:
            # Сохранение
            await calibrator.save_calibration_data()
            print("🎉 All motors calibrated successfully!")
        
    finally:
        await calibrator.disconnect()

async def main():
    """Главное меню"""
    
    print("🤖 ESP32 Robot Arm Calibration Menu")
    print("=" * 40)
    print("1. Quick calibration (interactive)")
    print("2. Calibrate single motor")
    print("3. Calibrate all motors")
    print("4. Test API connection")
    print("5. Exit")
    
    choice = input("\nChoose option (1-5): ").strip()
    
    if choice == "1":
        await quick_calibration()
    elif choice == "2":
        await calibrate_single_motor()
    elif choice == "3":
        await calibrate_all_motors()
    elif choice == "4":
        calibrator = EnhancedMotorCalibrator()
        await calibrator.test_api_connection()
    elif choice == "5":
        print("Goodbye!")
    else:
        print("Invalid choice!")

if __name__ == "__main__":
    asyncio.run(main())
