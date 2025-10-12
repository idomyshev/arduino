#!/usr/bin/env python3
"""
Simple Stop Test
Простой тест остановки моторов
"""

import asyncio
import sys
import os

# Добавляем родительскую папку в путь для импорта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from robot_arm_controller import RobotArmController

async def test_stop():
    """Простой тест остановки"""
    print("=" * 50)
    print("Simple Stop Test")
    print("=" * 50)
    
    controller = RobotArmController()
    
    try:
        # Подключаемся к ESP32
        device = await controller.scan_for_device()
        if not device:
            print("Device not found!")
            return False
            
        if not await controller.connect(device):
            print("Failed to connect!")
            return False
        
        print("Connected successfully!")
        
        print("\nStarting motor 0 forward...")
        await controller.send_command(0, "forward", 255)
        await controller.send_command(1, "forward", 250)
        await controller.send_command(2, "forward", 255)
        
        await asyncio.sleep(2)

        await controller.send_command(0, "forward", 0)

        await asyncio.sleep(2)

        await controller.send_command(1, "forward", 0)

        await asyncio.sleep(2)

        await controller.send_command(2, "forward", 0)
        
        # print("Stopping motor 0...")
        # result = await controller.send_command(0, "forward", 0)
        # print(f"Stop command result: {result}")
        
        # await asyncio.sleep(2)
        
        # print("Testing stop_all_motors...")
        # await controller.stop_all_motors()
        
        print("Test completed!")
        return True
        
    except Exception as e:
        print(f"Test failed: {e}")
        return False
    finally:
        await controller.disconnect()

if __name__ == "__main__":
    asyncio.run(test_stop())
