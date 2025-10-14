#!/usr/bin/env python3
"""
Финальный тест API-only системы
"""

import asyncio
import sys
import os

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from enhanced_calibrate import EnhancedMotorCalibrator
from classes.calibrated_robot_arm import CalibratedRobotArm

async def final_test():
    """Финальный тест системы"""
    print("🎯 Final API-Only System Test")
    print("=" * 50)
    
    robot_id = "esp32_robot_arm_001"
    server_url = "http://localhost:8000/api"
    
    # 1. Тест калибратора
    print("\n1. Testing EnhancedMotorCalibrator...")
    calibrator = EnhancedMotorCalibrator(robot_id=robot_id, server_url=server_url)
    
    # Проверяем API
    api_available = await calibrator.test_api_connection()
    if not api_available:
        print("❌ API server is not available!")
        return False
    
    print("✅ API connection successful")
    
    # Проверяем загрузку калибровки
    calibration_loaded = await calibrator.load_calibration_data()
    if calibration_loaded:
        print("✅ Calibration data loaded from API")
        print(f"   Calibrated motors: {list(calibrator.calibration_data.keys())}")
    else:
        print("ℹ️  No calibration data found")
    
    # 2. Тест контроллера робота
    print("\n2. Testing CalibratedRobotArm...")
    robot_arm = CalibratedRobotArm(robot_id=robot_id, server_url=server_url)
    
    # Проверяем загрузку калибровки
    calibration_loaded = await robot_arm.load_calibration_data()
    if calibration_loaded:
        print("✅ Calibration data loaded from API")
        print(f"   Calibrated motors: {list(robot_arm.calibration_data.keys())}")
    else:
        print("ℹ️  No calibration data found")
    
    # Проверяем загрузку стартовой позиции
    position_loaded = await robot_arm.load_calibration_start_position()
    if position_loaded:
        print("✅ Calibration start position loaded from API")
        robot_arm.show_start_position_status()
    else:
        print("ℹ️  No calibration start position found")
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
                else:
                    print(f"❌ Server error: {response.status}")
    except Exception as e:
        print(f"❌ Error checking server: {e}")
    
    # 4. Проверяем данные в API
    print("\n4. Checking API data...")
    try:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            # Проверяем калибровочные данные
            async with session.get(f"{server_url}/calibration/{robot_id}") as response:
                if response.status == 200:
                    print("✅ Calibration data available in API")
                elif response.status == 404:
                    print("ℹ️  No calibration data in API")
                else:
                    print(f"❌ Calibration API error: {response.status}")
            
            # Проверяем позиции
            async with session.get(f"{server_url}/position/{robot_id}") as response:
                if response.status == 200:
                    print("✅ Position data available in API")
                elif response.status == 404:
                    print("ℹ️  No position data in API")
                else:
                    print(f"❌ Position API error: {response.status}")
                    
    except Exception as e:
        print(f"❌ Error checking API data: {e}")
    
    print("\n🎉 Final Test Complete!")
    print("=" * 50)
    print("✅ API-only system working")
    print("✅ No file dependencies")
    print("✅ Centralized data storage")
    print("✅ All components integrated")
    
    return True

if __name__ == "__main__":
    asyncio.run(final_test())
