#!/usr/bin/env python3
"""
Auto Calibration Script
Автоматическая калибровка без интерактивного ввода
"""

import asyncio
import sys
import os

# Добавляем путь к классам
sys.path.append(os.path.join(os.path.dirname(__file__), 'classes'))

from enhanced_calibrate import EnhancedMotorCalibrator

async def auto_calibration():
    """Автоматическая калибровка с настройками по умолчанию"""
    
    print("🤖 ESP32 Robot Arm - Auto Calibration")
    print("=" * 50)
    
    calibrator = EnhancedMotorCalibrator(
        robot_id="esp32_robot_arm_001",
        server_url="http://localhost:8000/api",
        use_api=True,
        fallback_to_file=True
    )
    
    # Проверяем API
    print("Checking API connection...")
    api_available = await calibrator.test_api_connection()
    
    if not api_available:
        calibrator.use_api = False
        calibrator.fallback_to_file = True
        print("Using file-only mode")
    
    # Подключаемся к роботу
    print("\nConnecting to robot...")
    if not await calibrator.connect():
        print("❌ Failed to connect to robot!")
        print("Make sure:")
        print("  - ESP32 is powered on")
        print("  - Bluetooth is enabled")
        print("  - Robot is in range")
        return False
    
    try:
        print("✅ Connected to robot!")
        
        # Загружаем существующие данные
        await calibrator.load_calibration_data()
        
        # Показываем текущий статус
        calibrator.show_calibration_status()
        
        # Выбираем режим калибровки
        print("\nCalibration options:")
        print("1. Calibrate all motors")
        print("2. Calibrate single motor")
        print("3. Recalibrate existing motor")
        
        # Для автоматического режима выбираем калибровку всех моторов
        choice = "1"  # Автоматически выбираем калибровку всех моторов
        speed = 150   # Скорость по умолчанию
        
        print(f"Auto-selected: Calibrate all motors at speed {speed}")
        
        if choice == "1":
            print("\nStarting calibration of all motors...")
            success = await calibrator.calibrate_all_motors(speed)
            
            if success:
                print("🎉 All motors calibrated successfully!")
                
                # Сохраняем калибровочные данные
                print("\nSaving calibration data...")
                await calibrator.save_calibration_data()
                
                # Сохраняем стартовую позицию
                print("Saving calibration start position...")
                await calibrator.save_calibration_start_position()
                
                print("✅ Calibration completed and saved successfully!")
            else:
                print("❌ Calibration failed!")
                return False
        
        # Показываем финальный статус
        print("\nFinal calibration status:")
        calibrator.show_calibration_status()
        
        return True
        
    except Exception as e:
        print(f"❌ Calibration error: {e}")
        return False
    finally:
        await calibrator.disconnect()
        print("Disconnected from robot")

async def main():
    """Основная функция"""
    
    print("Starting automatic calibration...")
    print("This will calibrate all motors and save the start position.")
    print("Make sure the robot is ready!")
    
    success = await auto_calibration()
    
    if success:
        print("\n🎉 CALIBRATION COMPLETED SUCCESSFULLY!")
        print("=" * 50)
        print("Next steps:")
        print("1. Test the robot with: python3 examples/example_calibrated.py")
        print("2. Verify start position is loaded correctly")
        print("3. Try some movements to test accuracy")
    else:
        print("\n❌ CALIBRATION FAILED!")
        print("Check the error messages above and try again.")

if __name__ == "__main__":
    asyncio.run(main())
