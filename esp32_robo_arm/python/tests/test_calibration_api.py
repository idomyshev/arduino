#!/usr/bin/env python3
"""
Test Enhanced Calibration API
Тест API калибровки
"""

import asyncio
import sys
import os

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from enhanced_calibrate import EnhancedMotorCalibrator

async def test_api():
    """Тест API подключения"""
    print("🧪 Testing Enhanced Calibration API")
    print("=" * 40)
    
    calibrator = EnhancedMotorCalibrator(
        robot_id="esp32_robot_arm_001",
        server_url="http://localhost:8000/api"
    )
    
    # Тест подключения к API
    print("Testing API connection...")
    success = await calibrator.test_api_connection()
    
    if success:
        print("✅ API is working!")
        
        # Тест загрузки данных
        print("\nTesting data loading...")
        try:
            await calibrator.load_calibration_data()
            print("✅ Data loading successful!")
            
            # Показ статуса
            calibrator.show_calibration_status()
            
        except Exception as e:
            print(f"❌ Data loading failed: {e}")
    else:
        print("❌ API is not available!")
        print("Make sure server is running: cd python/server && python3 data_server.py")

if __name__ == "__main__":
    asyncio.run(test_api())
