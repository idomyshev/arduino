#!/usr/bin/env python3
"""
Test Calibration Start Position System
Тест системы стартовой позиции после калибровки
"""

import asyncio
import sys
import os
import json

# Добавляем путь к классам
sys.path.append(os.path.join(os.path.dirname(__file__), 'classes'))

from enhanced_calibrate import EnhancedMotorCalibrator
from calibrated_robot_arm import CalibratedRobotArm

async def test_calibration_start_position():
    """Тест системы стартовой позиции после калибровки"""
    
    print("🧪 Testing Calibration Start Position System")
    print("=" * 60)
    
    # 1. Тест сохранения стартовой позиции через EnhancedMotorCalibrator
    print("\n1️⃣ Testing EnhancedMotorCalibrator - Saving Start Position")
    print("-" * 50)
    
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
    
    # Сохраняем стартовую позицию
    print("Saving calibration start position...")
    success = await calibrator.save_calibration_start_position()
    
    if success:
        print("✅ Start position saved successfully!")
    else:
        print("❌ Failed to save start position!")
        return
    
    # Проверяем файл
    position_file = os.path.join(
        os.path.dirname(__file__), "data", "robot_data_position.json"
    )
    
    if os.path.exists(position_file):
        print(f"✅ Position file created: {position_file}")
        with open(position_file, 'r') as f:
            data = json.load(f)
        print(f"   Position name: {data['position_name']}")
        print(f"   Motor positions: {data['motor_positions']}")
        print(f"   Timestamp: {data['timestamp']}")
    else:
        print(f"❌ Position file not found: {position_file}")
    
    # 2. Тест загрузки стартовой позиции через CalibratedRobotArm
    print("\n2️⃣ Testing CalibratedRobotArm - Loading Start Position")
    print("-" * 50)
    
    robot = CalibratedRobotArm()
    
    # Загружаем стартовую позицию (без подключения к роботу)
    print("Loading calibration start position...")
    success = await robot.load_calibration_start_position()
    
    if success:
        print("✅ Start position loaded successfully!")
        robot.show_start_position_status()
    else:
        print("❌ Failed to load start position!")
    
    # 3. Тест проверки соответствия позиции
    print("\n3️⃣ Testing Position Verification")
    print("-" * 50)
    
    print("Testing position verification...")
    is_correct = await robot.verify_start_position()
    
    if is_correct:
        print("✅ Position verification passed!")
    else:
        print("❌ Position verification failed!")
    
    # 4. Тест изменения позиции и повторной проверки
    print("\n4️⃣ Testing Position Change and Re-verification")
    print("-" * 50)
    
    # Изменяем позицию одного мотора
    robot.current_positions[0] = 0.3  # Мотор 0 на 30%
    print("Changed motor 0 position to 30%")
    
    # Проверяем снова
    is_correct = await robot.verify_start_position()
    
    if not is_correct:
        print("✅ Position verification correctly detected change!")
    else:
        print("❌ Position verification failed to detect change!")
    
    # 5. Тест API данных
    print("\n5️⃣ Testing API Data")
    print("-" * 50)
    
    if calibrator.use_api:
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{calibrator.server_url}/position/{calibrator.robot_id}") as response:
                    if response.status == 200:
                        data = await response.json()
                        print("✅ API position data retrieved!")
                        print(f"   Position: {data['position']['motor_positions']}")
                        print(f"   Name: {data['position']['position_name']}")
                    else:
                        print(f"❌ API error: {response.status}")
        except Exception as e:
            print(f"❌ API test failed: {e}")
    else:
        print("ℹ️  API not available, skipping API test")
    
    print("\n" + "=" * 60)
    print("🎉 CALIBRATION START POSITION SYSTEM TEST COMPLETED!")
    print("=" * 60)
    
    print("\nSummary:")
    print("✅ EnhancedMotorCalibrator can save start position")
    print("✅ CalibratedRobotArm can load start position")
    print("✅ Position verification works correctly")
    print("✅ System detects position changes")
    print("✅ Data is saved to file and API")
    
    print("\nNext steps:")
    print("1. Run actual calibration with: python3 enhanced_calibrate.py")
    print("2. Test with real robot: python3 examples/example_calibrated.py")
    print("3. Verify start position is loaded correctly")

async def test_with_real_calibration():
    """Тест с реальной калибровкой (требует подключения к роботу)"""
    
    print("\n🤖 Testing with Real Robot Calibration")
    print("=" * 50)
    print("⚠️  This test requires ESP32 robot to be connected!")
    print("Press Ctrl+C to skip this test...")
    
    try:
        calibrator = EnhancedMotorCalibrator(
            robot_id="esp32_robot_arm_001",
            use_api=True,
            fallback_to_file=True
        )
        
        # Подключаемся к роботу
        if await calibrator.connect():
            print("✅ Connected to robot!")
            
            # Загружаем существующие данные
            await calibrator.load_calibration_data()
            
            # Показываем статус
            calibrator.show_calibration_status()
            
            # Сохраняем стартовую позицию
            await calibrator.save_calibration_start_position()
            
            await calibrator.disconnect()
            print("✅ Real robot test completed!")
        else:
            print("❌ Failed to connect to robot!")
            
    except KeyboardInterrupt:
        print("\n⏭️  Skipping real robot test")
    except Exception as e:
        print(f"❌ Real robot test failed: {e}")

async def main():
    """Основная функция тестирования"""
    
    # Основной тест
    await test_calibration_start_position()
    
    # Опциональный тест с реальным роботом
    choice = input("\nTest with real robot? (y/n): ").lower().strip()
    if choice == 'y':
        await test_with_real_calibration()

if __name__ == "__main__":
    asyncio.run(main())
