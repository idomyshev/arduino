#!/usr/bin/env python3
"""
ESP32 Robot Arm BLE Controller
Управление робо-рукой ESP32 через Bluetooth Low Energy с Mac
"""

import asyncio
import json
import sys
from bleak import BleakClient, BleakScanner
from bleak.backends.scanner import AdvertisementData
from bleak.backends.device import BLEDevice

# BLE настройки (должны совпадать с ESP32)
SERVICE_UUID = "12345678-1234-1234-1234-123456789abc"
CHARACTERISTIC_UUID = "87654321-4321-4321-4321-cba987654321"
DEVICE_NAME = "ESP32-RobotArm"

class RobotArmController:
    def __init__(self):
        self.client = None
        self.connected = False
        
    async def scan_for_device(self):
        """Поиск устройства ESP32-RobotArm"""
        print("Scanning for ESP32 Robot Arm...")
        
        devices = await BleakScanner.discover(timeout=10.0)
        
        for device in devices:
            if device.name and DEVICE_NAME in device.name:
                print(f"Found device: {device.name} ({device.address})")
                return device
                
        print("Device not found!")
        return None
    
    async def connect(self, device):
        """Подключение к устройству"""
        try:
            self.client = BleakClient(device.address)
            await self.client.connect()
            self.connected = True
            print(f"Connected to {device.name}")
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False
    
    async def disconnect(self):
        """Отключение от устройства"""
        if self.client and self.connected:
            await self.client.disconnect()
            self.connected = False
            print("Disconnected")
    
    async def send_command(self, motor, direction, speed):
        """Отправка команды управления мотором"""
        if not self.connected:
            print("Not connected to device!")
            return False
            
        # Создаем JSON команду
        command = {
            "motor": motor,      # 0, 1, 2 для M1, M2, M3
            "direction": direction,  # "forward" или "backward"
            "speed": speed       # 0-255
        }
        
        json_command = json.dumps(command)
        print(f"Sending command: {json_command}")
        
        try:
            await self.client.write_gatt_char(CHARACTERISTIC_UUID, json_command.encode())
            return True
        except Exception as e:
            print(f"Failed to send command: {e}")
            return False
    
    async def stop_all_motors(self):
        """Остановка всех моторов"""
        print("Stopping all motors...")
        for motor in range(3):
            await self.send_command(motor, "forward", 0)
    
    async def demo_sequence(self):
        """Демонстрационная последовательность движений"""
        print("Starting demo sequence...")
        
        # Демо: поочередное движение моторов
        for motor in range(3):
            print(f"Moving motor {motor} forward...")
            await self.send_command(motor, "forward", 150)
            await asyncio.sleep(2)
            
            print(f"Moving motor {motor} backward...")
            await self.send_command(motor, "backward", 150)
            await asyncio.sleep(2)
            
            print(f"Stopping motor {motor}...")
            await self.send_command(motor, "forward", 0)
            await asyncio.sleep(1)
        
        # Демо: синхронное движение всех моторов
        print("Synchronized movement...")
        await self.send_command(0, "forward", 100)
        await self.send_command(1, "backward", 100)
        await self.send_command(2, "forward", 100)
        await asyncio.sleep(3)
        
        await self.stop_all_motors()
        print("Demo completed!")

def print_help():
    """Вывод справки по командам"""
    print("""
ESP32 Robot Arm BLE Controller

Команды:
  python robot_arm_controller.py scan          - Поиск устройства
  python robot_arm_controller.py connect      - Подключение и интерактивный режим
  python robot_arm_controller.py demo         - Демонстрационная последовательность
  
Интерактивные команды (после подключения):
  m <motor> <direction> <speed>  - Управление мотором
                                   motor: 0, 1, 2 (M1, M2, M3)
                                   direction: forward, backward
                                   speed: 0-255
  stop                           - Остановить все моторы
  help                           - Показать справку
  quit                           - Выход

Примеры:
  m 0 forward 150               - M1 вперед со скоростью 150
  m 1 backward 100              - M2 назад со скоростью 100
  m 2 forward 255               - M3 вперед на максимальной скорости
""")

async def interactive_mode(controller):
    """Интерактивный режим управления"""
    print("Interactive mode. Type 'help' for commands, 'quit' to exit.")
    
    while controller.connected:
        try:
            command = input("Robot> ").strip().lower()
            
            if command == "quit":
                break
            elif command == "help":
                print_help()
            elif command == "stop":
                await controller.stop_all_motors()
            elif command.startswith("m "):
                # Команда управления мотором: m <motor> <direction> <speed>
                parts = command.split()
                if len(parts) == 4:
                    try:
                        motor = int(parts[1])
                        direction = parts[2]
                        speed = int(parts[3])
                        
                        if motor < 0 or motor > 2:
                            print("Motor must be 0, 1, or 2")
                            continue
                            
                        if direction not in ["forward", "backward"]:
                            print("Direction must be 'forward' or 'backward'")
                            continue
                            
                        if speed < 0 or speed > 255:
                            print("Speed must be 0-255")
                            continue
                            
                        await controller.send_command(motor, direction, speed)
                    except ValueError:
                        print("Invalid motor or speed value")
                else:
                    print("Usage: m <motor> <direction> <speed>")
            else:
                print("Unknown command. Type 'help' for available commands.")
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")

async def main():
    """Основная функция"""
    if len(sys.argv) < 2:
        print_help()
        return
    
    command = sys.argv[1].lower()
    controller = RobotArmController()
    
    try:
        if command == "scan":
            device = await controller.scan_for_device()
            if device:
                print(f"Device found: {device.name} at {device.address}")
            
        elif command == "connect":
            device = await controller.scan_for_device()
            if device:
                if await controller.connect(device):
                    await interactive_mode(controller)
            
        elif command == "demo":
            device = await controller.scan_for_device()
            if device:
                if await controller.connect(device):
                    await controller.demo_sequence()
            
        else:
            print("Unknown command. Use 'scan', 'connect', or 'demo'")
            
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await controller.disconnect()

if __name__ == "__main__":
    # Проверяем наличие библиотеки bleak
    try:
        import bleak
    except ImportError:
        print("Error: bleak library not found!")
        print("Install it with: pip install bleak")
        sys.exit(1)
    
    asyncio.run(main())
