#!/usr/bin/env python3
"""
Debug Test: File Saving Issue
Тест для отладки проблемы с сохранением файла
"""

import asyncio
import sys
import os
import json
from datetime import datetime
from dataclasses import asdict

# Добавляем путь к классам
sys.path.append(os.path.join(os.path.dirname(__file__), 'classes'))

from enhanced_calibrate import EnhancedMotorCalibrator

async def debug_file_saving():
    """Отладка сохранения файла"""
    
    print("🔍 Debug: File Saving Issue")
    print("=" * 40)
    
    calibrator = EnhancedMotorCalibrator(
        robot_id="esp32_robot_arm_001",
        use_api=False,  # Только файл
        fallback_to_file=True
    )
    
    # Создаем тестовую позицию
    start_position = {
        0: 0.0,  # Мотор 0 в минимальной позиции
        1: 0.0,  # Мотор 1 в минимальной позиции  
        2: 0.0   # Мотор 2 в минимальной позиции
    }
    
    from classes.data_storage_manager import RobotPosition
    position = RobotPosition(
        timestamp=datetime.now().isoformat(),
        motor_positions=start_position,
        position_name="calibration_start"
    )
    
    print(f"Created position: {asdict(position)}")
    
    # Сохраняем в файл
    print("Saving to file...")
    await calibrator._save_position_to_file(position)
    
    # Проверяем файл
    position_file = os.path.join(
        os.path.dirname(__file__), "data", "robot_data_position.json"
    )
    
    print(f"Checking file: {position_file}")
    
    if os.path.exists(position_file):
        with open(position_file, 'r') as f:
            data = json.load(f)
        print(f"File contents: {data}")
        
        if data['position_name'] == 'calibration_start':
            print("✅ File saved correctly!")
        else:
            print(f"❌ File has wrong position_name: {data['position_name']}")
    else:
        print("❌ File not found!")

if __name__ == "__main__":
    asyncio.run(debug_file_saving())
