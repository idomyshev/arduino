#!/usr/bin/env python3
"""
Test Enhanced Calibration Data Saving
Тест сохранения данных калибровки
"""

import asyncio
import sys
import os
import json

# Добавляем путь к классам
sys.path.append(os.path.join(os.path.dirname(__file__), 'classes'))

from enhanced_calibrate import EnhancedMotorCalibrator

async def test_data_saving():
    """Тест сохранения данных калибровки"""
    print("🧪 Testing Enhanced Calibration Data Saving")
    print("=" * 50)
    
    calibrator = EnhancedMotorCalibrator(
        robot_id="esp32_robot_arm_001",
        server_url="http://localhost:8000/api",
        use_api=True,
        fallback_to_file=True
    )
    
    print(f"Robot ID: {calibrator.robot_id}")
    print(f"Server URL: {calibrator.server_url}")
    print(f"Use API: {calibrator.use_api}")
    print(f"Fallback to file: {calibrator.fallback_to_file}")
    print(f"Calibration file path: {calibrator.calibration_file}")
    print()
    
    # Тест подключения к API
    print("Testing API connection...")
    api_available = await calibrator.test_api_connection()
    
    if api_available:
        print("✅ API is available")
    else:
        print("❌ API is not available")
        calibrator.use_api = False
        calibrator.fallback_to_file = True
        print("Switching to file-only mode")
    
    # Создаем тестовые данные калибровки
    print("\nCreating test calibration data...")
    test_data = {
        0: {
            "calibrated": True,
            "calibration_date": "2025-01-14T15:30:00",
            "forward_time": 9.5,
            "backward_time": 14.8,
            "speed": 150,
            "positions": {
                "min": None,
                "max": None
            },
            "return_time": 3.9,
            "total_travel_time": 24.3,
            "average_travel_time": 12.15
        },
        1: {
            "calibrated": True,
            "calibration_date": "2025-01-14T15:31:00",
            "forward_time": 25.2,
            "backward_time": 43.6,
            "speed": 150,
            "positions": {
                "min": None,
                "max": None
            },
            "return_time": 32.1,
            "total_travel_time": 68.8,
            "average_travel_time": 34.4
        }
    }
    
    calibrator.calibration_data = test_data
    
    # Сохраняем данные
    print("\nSaving calibration data...")
    success = await calibrator.save_calibration_data()
    
    if success:
        print("✅ Data saved successfully!")
    else:
        print("❌ Data saving failed!")
    
    # Проверяем файл
    print(f"\nChecking file: {calibrator.calibration_file}")
    if os.path.exists(calibrator.calibration_file):
        print("✅ File exists")
        with open(calibrator.calibration_file, 'r') as f:
            file_data = json.load(f)
        print(f"File contains {len(file_data)} motors")
        for motor_id, data in file_data.items():
            print(f"  Motor {motor_id}: {'✅' if data['calibrated'] else '❌'}")
    else:
        print("❌ File does not exist")
    
    # Проверяем API
    if calibrator.use_api:
        print(f"\nChecking API data...")
        try:
            await calibrator.load_calibration_data()
            print("✅ API data loaded successfully")
            print(f"Loaded {len(calibrator.calibration_data)} motors")
        except Exception as e:
            print(f"❌ API data loading failed: {e}")
    
    print("\n" + "=" * 50)
    print("SUMMARY:")
    print(f"File path: {calibrator.calibration_file}")
    print(f"File exists: {os.path.exists(calibrator.calibration_file)}")
    print(f"API enabled: {calibrator.use_api}")
    print(f"Fallback enabled: {calibrator.fallback_to_file}")

if __name__ == "__main__":
    asyncio.run(test_data_saving())
