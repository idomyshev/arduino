#!/usr/bin/env python3
"""
Motor Calibration Launcher
Запуск калибровки моторов робо-руки
"""

import asyncio
import sys
import os

# Добавляем папку classes в путь для импорта
sys.path.append(os.path.join(os.path.dirname(__file__), 'classes'))
from motor_calibration import MotorCalibrator

async def main():
    """Запуск калибровки"""
    print("ESP32 Robot Arm - Motor Calibration")
    print("=" * 40)
    
    calibrator = MotorCalibrator()
    await calibrator.interactive_calibration()

if __name__ == "__main__":
    asyncio.run(main())
