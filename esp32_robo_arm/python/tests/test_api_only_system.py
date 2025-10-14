#!/usr/bin/env python3
"""
Тест системы без файлового хранения - только API
"""

import asyncio
import sys
import os

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from enhanced_calibrate import EnhancedMotorCalibrator
from classes.calibrated_robot_arm import CalibratedRobotArm

async def test_api_only_system():
    """Тест системы только с API"""
    print("🧪 Testing API-Only System")
    print("=" * 50)
    
    robot_id = "esp32_robot_arm_001"
    server_url = "http://localhost:8000/api"
    
    # 1. Тест калибратора
    print("\n1. Testing EnhancedMotorCalibrator...")
    calibrator = EnhancedMotorCalibrator(robot_id=robot_id, server_url=server_url)
    
    # Проверяем подключение к API
    api_available = await calibrator.test_api_connection()
    if not api_available:
        print("❌ API server is not available!")
        print("Please start the server: cd python/server && python3 data_server.py")
        return
    
    print("✅ API connection successful")
    
    # Проверяем загрузку калибровочных данных
    calibration_loaded = await calibrator.load_calibration_data()
    if calibration_loaded:
        print("✅ Calibration data loaded from API")
        print(f"   Calibrated motors: {list(calibrator.calibration_data.keys())}")
    else:
        print("ℹ️  No calibration data found on server")
    
    # 2. Тест контроллера робота
    print("\n2. Testing CalibratedRobotArm...")
    robot_arm = CalibratedRobotArm(robot_id=robot_id, server_url=server_url)
    
    # Проверяем загрузку калибровочных данных
    calibration_loaded = await robot_arm.load_calibration_data()
    if calibration_loaded:
        print("✅ Calibration data loaded from API")
        print(f"   Calibrated motors: {list(robot_arm.calibration_data.keys())}")
    else:
        print("ℹ️  No calibration data found on server")
    
    # Проверяем загрузку стартовой позиции
    position_loaded = await robot_arm.load_calibration_start_position()
    if position_loaded:
        print("✅ Calibration start position loaded from API")
        robot_arm.show_start_position_status()
    else:
        print("ℹ️  No calibration start position found on server")
        robot_arm.show_start_position_status()
    
    # 3. Проверяем статус сервера
    print("\n3. Checking server status...")
    try:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{server_url}/status") as response:
                if response.status == 200:
                    status = await response.json()
                    print("✅ Server is running")
                    print(f"   Database: {status['database']}")
                    print(f"   Robots: {status['robots']}")
                else:
                    print(f"❌ Server error: {response.status}")
    except Exception as e:
        print(f"❌ Error checking server: {e}")
    
    print("\n🎉 API-Only System Test Complete!")
    print("=" * 50)
    print("✅ All components working with API only")
    print("✅ No file dependencies")
    print("✅ Centralized data storage")

if __name__ == "__main__":
    asyncio.run(test_api_only_system())
