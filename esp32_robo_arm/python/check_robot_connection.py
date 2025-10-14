#!/usr/bin/env python3
"""
Pre-Calibration Checklist
Чек-лист перед калибровкой
"""

import asyncio
import sys
import os

# Добавляем путь к классам
sys.path.append(os.path.join(os.path.dirname(__file__), 'classes'))

from enhanced_calibrate import EnhancedMotorCalibrator

async def check_robot_connection():
    """Проверка подключения к роботу"""
    
    print("🔍 ESP32 Robot Arm - Connection Check")
    print("=" * 50)
    
    calibrator = EnhancedMotorCalibrator()
    
    print("Checking API server...")
    api_available = await calibrator.test_api_connection()
    
    if api_available:
        print("✅ API server is running")
    else:
        print("❌ API server is not available")
        print("Start server with: cd python/server && python3 data_server.py")
        return False
    
    print("\nScanning for ESP32 Robot Arm...")
    device = await calibrator.controller.scan_for_device()
    
    if device:
        print(f"✅ Found device: {device.name} ({device.address})")
        
        print("\nAttempting connection...")
        if await calibrator.controller.connect(device):
            print("✅ Successfully connected to robot!")
            
            # Тестируем отправку команды
            print("\nTesting motor command...")
            result = await calibrator.controller.send_command(0, "forward", 100, 1000)
            
            if result:
                print("✅ Motor command sent successfully!")
                print("Robot is ready for calibration!")
            else:
                print("❌ Failed to send motor command")
            
            await calibrator.controller.disconnect()
            return True
        else:
            print("❌ Failed to connect to device")
            return False
    else:
        print("❌ ESP32 Robot Arm not found!")
        print("\nTroubleshooting checklist:")
        print("1. ✅ Is ESP32 powered on?")
        print("2. ✅ Is Bluetooth enabled on your Mac?")
        print("3. ✅ Is robot in range (within 10 meters)?")
        print("4. ✅ Is ESP32 running the correct firmware?")
        print("5. ✅ Is robot in pairing mode?")
        return False

async def main():
    """Основная функция проверки"""
    
    print("🤖 ESP32 Robot Arm - Pre-Calibration Check")
    print("=" * 60)
    
    success = await check_robot_connection()
    
    if success:
        print("\n🎉 ROBOT IS READY FOR CALIBRATION!")
        print("=" * 40)
        print("You can now run:")
        print("  python3 auto_calibrate.py")
        print("\nOr for interactive calibration:")
        print("  python3 enhanced_calibrate.py")
    else:
        print("\n⚠️  ROBOT IS NOT READY!")
        print("=" * 30)
        print("Please fix the issues above before calibration.")
        print("\nWhen ready, run this check again:")
        print("  python3 check_robot_connection.py")

if __name__ == "__main__":
    asyncio.run(main())
