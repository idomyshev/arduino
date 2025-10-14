#!/usr/bin/env python3
"""
Example: Enhanced Robot Arm with Position Storage
Пример использования улучшенного контроллера с сохранением позиций
"""

import asyncio
import sys
import os

# Добавляем путь к классам
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'classes'))

from enhanced_calibrated_robot_arm import EnhancedCalibratedRobotArm, StorageType

async def main():
    """Основная функция демонстрации"""
    
    print("=" * 60)
    print("ENHANCED ROBOT ARM WITH POSITION STORAGE")
    print("=" * 60)
    
    # Создаем контроллер с гибридным хранением данных
    robot = EnhancedCalibratedRobotArm(
        robot_id="esp32_robot_arm_001",
        storage_type=StorageType.HYBRID,  # Локально + сервер
        server_url="http://localhost:8000/api"  # URL сервера
    )
    
    print(f"Robot ID: {robot.robot_id}")
    print(f"Storage Type: {robot.storage_type.value}")
    print()
    
    # Подключаемся к роботу
    print("Connecting to robot...")
    if not await robot.connect():
        print("❌ Failed to connect to robot!")
        print("Make sure:")
        print("  - ESP32 is powered on")
        print("  - Bluetooth is enabled")
        print("  - Robot is in range")
        return
    
    print("✅ Connected to robot!")
    print()
    
    # Показываем статус калибровки
    robot.show_calibration_status()
    
    # Показываем текущие позиции (загруженные из сохранения)
    robot.show_current_positions()
    
    # Показываем доступные позиции
    robot.show_available_positions()
    
    # Демонстрация движений с сохранением позиций
    print("=" * 40)
    print("DEMONSTRATION: MOVEMENTS WITH POSITION SAVING")
    print("=" * 40)
    
    # 1. Переход в позицию "home"
    print("\n1. Moving to HOME position...")
    await robot.move_to_position("home", save_position=True)
    await asyncio.sleep(2)
    
    # 2. Переход в позицию "pick"
    print("\n2. Moving to PICK position...")
    await robot.move_to_position("pick", save_position=True)
    await asyncio.sleep(2)
    
    # 3. Плавное движение мотора 0
    print("\n3. Smooth movement of motor 0...")
    await robot.smooth_move(0, 0.3, 0.7, steps=5, step_delay=0.3)
    await asyncio.sleep(1)
    
    # 4. Переход в позицию "place"
    print("\n4. Moving to PLACE position...")
    await robot.move_to_position("place", save_position=True)
    await asyncio.sleep(2)
    
    # 5. Возврат в "home"
    print("\n5. Returning to HOME position...")
    await robot.move_to_position("home", save_position=True)
    await asyncio.sleep(2)
    
    # Показываем финальные позиции
    print("\n" + "=" * 40)
    print("FINAL POSITIONS")
    print("=" * 40)
    robot.show_current_positions()
    
    # Получаем историю позиций
    print("\n" + "=" * 40)
    print("POSITION HISTORY")
    print("=" * 40)
    try:
        history = await robot.get_position_history(limit=10)
        if history:
            print(f"Found {len(history)} recent positions:")
            for i, pos in enumerate(history[:5]):  # Показываем только последние 5
                print(f"  {i+1}. {pos.position_name or 'custom'} - {pos.timestamp}")
                print(f"     Motors: {pos.motor_positions}")
        else:
            print("No position history found")
    except Exception as e:
        print(f"Error getting history: {e}")
    
    # Синхронизация данных с сервером
    print("\n" + "=" * 40)
    print("DATA SYNCHRONIZATION")
    print("=" * 40)
    try:
        sync_result = await robot.sync_data()
        if sync_result:
            print("✅ Data synchronized successfully")
        else:
            print("⚠️  Data synchronization failed (server may be offline)")
    except Exception as e:
        print(f"❌ Sync error: {e}")
    
    # Отключаемся (позиция автоматически сохранится)
    print("\n" + "=" * 40)
    print("DISCONNECTING")
    print("=" * 40)
    await robot.disconnect()
    print("✅ Disconnected. Position saved automatically.")
    
    print("\n" + "=" * 60)
    print("DEMONSTRATION COMPLETED")
    print("=" * 60)
    print("\nKey Features Demonstrated:")
    print("✅ Automatic position saving")
    print("✅ Position loading on connect")
    print("✅ Hybrid storage (local + server)")
    print("✅ Position history tracking")
    print("✅ Data synchronization")
    print("✅ Smooth movements")
    print("✅ Predefined positions")

async def test_storage_only():
    """Тест только системы хранения без подключения к роботу"""
    
    print("=" * 60)
    print("STORAGE SYSTEM TEST")
    print("=" * 60)
    
    from data_storage_manager import RobotDataStorage, StorageType, MotorCalibrationData, RobotPosition
    from datetime import datetime
    
    # Создаем менеджер хранения
    storage = RobotDataStorage(
        robot_id="test_robot_001",
        storage_type=StorageType.HYBRID
    )
    
    # Тестовые калибровочные данные
    calibration_data = {
        0: MotorCalibrationData(
            motor_id=0,
            calibrated=True,
            calibration_date=datetime.now().isoformat(),
            forward_time=9.2,
            backward_time=14.4,
            speed=150
        ),
        1: MotorCalibrationData(
            motor_id=1,
            calibrated=True,
            calibration_date=datetime.now().isoformat(),
            forward_time=25.1,
            backward_time=43.4,
            speed=150
        )
    }
    
    # Сохраняем калибровочные данные
    print("Saving calibration data...")
    await storage.save_calibration_data(calibration_data)
    
    # Тестовая позиция
    test_position = RobotPosition(
        timestamp=datetime.now().isoformat(),
        motor_positions={0: 0.5, 1: 0.3, 2: 0.7},
        position_name="test_position"
    )
    
    # Сохраняем позицию
    print("Saving test position...")
    await storage.save_current_position(test_position)
    
    # Загружаем данные
    print("Loading data...")
    loaded_calibration = await storage.load_calibration_data()
    loaded_position = await storage.load_current_position()
    
    print(f"✅ Loaded {len(loaded_calibration)} calibrated motors")
    print(f"✅ Loaded position: {loaded_position.position_name}")
    print(f"   Motor positions: {loaded_position.motor_positions}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "storage":
        # Тест только системы хранения
        asyncio.run(test_storage_only())
    else:
        # Полная демонстрация
        asyncio.run(main())
