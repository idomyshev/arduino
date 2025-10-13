#!/usr/bin/env python3
"""
Example: Using Calibrated Robot Arm
Пример использования откалиброванной робо-руки
"""

import asyncio
import sys
import os

# Добавляем родительскую папку в путь для импорта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from classes.calibrated_robot_arm import CalibratedRobotArm

async def demo_calibrated_movements():
    """Демонстрация откалиброванных движений"""
    print("=" * 60)
    print("CALIBRATED ROBOT ARM DEMO")
    print("=" * 60)
    
    robot = CalibratedRobotArm()
    
    try:
        if not await robot.connect():
            print("Failed to connect!")
            return False
        
        # Показываем статус калибровки
        robot.show_calibration_status()
        
        # Показываем доступные позиции
        robot.show_available_positions()
        
        print("\nStarting demo sequences...")
        
        # Демо 1: Переходы между позициями
        print("\n1. Position transitions demo:")
        await robot.move_to_position("pick")
        await asyncio.sleep(2)

        await robot.move_to_position("home")
        await asyncio.sleep(2)
        
        await robot.move_to_position("pick")
        await asyncio.sleep(2)

        await robot.move_to_position("home")
        await asyncio.sleep(2)
        
        await robot.move_to_position("place")
        await asyncio.sleep(2)

        await robot.move_to_position("home")
        await asyncio.sleep(2)
        
        await robot.move_to_position("rest")
        await asyncio.sleep(2)
        
        # Демо 2: Точное позиционирование
        print("\n2. Precise positioning demo:")
        await robot.move_to_percentage(0, 0.0)    # Минимум
        await asyncio.sleep(1)
        await robot.move_to_percentage(0, 0.5)    # Середина
        await asyncio.sleep(1)
        await robot.move_to_percentage(0, 1.0)    # Максимум
        await asyncio.sleep(1)
        await robot.move_to_percentage(0, 0.25)   # 25%
        await asyncio.sleep(1)
        
        # Демо 3: Плавное движение
        print("\n3. Smooth movement demo:")
        await robot.smooth_move(0, 0.0, 1.0, steps=20, step_delay=0.1)
        await robot.smooth_move(0, 1.0, 0.0, steps=20, step_delay=0.1)
        
        # Демо 4: Готовые последовательности
        print("\n4. Pick and place sequence:")
        await robot.pick_and_place_sequence()
        
        print("\n5. Wave sequence:")
        await robot.wave_sequence()
        
        # Возврат в исходное положение
        await robot.move_to_position("home")
        
        print("\nDemo completed successfully!")
        return True
        
    except Exception as e:
        print(f"Demo failed: {e}")
        return False
    finally:
        await robot.disconnect()

async def interactive_calibrated_mode():
    """Интерактивный режим с откалиброванными движениями"""
    print("=" * 60)
    print("INTERACTIVE CALIBRATED ROBOT ARM")
    print("=" * 60)
    
    robot = CalibratedRobotArm()
    
    try:
        if not await robot.connect():
            return False
        
        robot.show_calibration_status()
        
        print("\nAvailable commands:")
        print("  move <motor> <percentage>  - Move motor to percentage (0.0-1.0)")
        print("  position <name>            - Move to predefined position")
        print("  smooth <motor> <start> <end> - Smooth move between percentages")
        print("  pickplace                  - Run pick and place sequence")
        print("  wave                       - Run wave sequence")
        print("  status                     - Show calibration status")
        print("  positions                  - Show available positions")
        print("  quit                       - Exit")
        
        while True:
            try:
                command = input("\nCalibrated> ").strip().lower()
                
                if command == "quit":
                    break
                elif command == "status":
                    robot.show_calibration_status()
                elif command == "positions":
                    robot.show_available_positions()
                elif command == "pickplace":
                    await robot.pick_and_place_sequence()
                elif command == "wave":
                    await robot.wave_sequence()
                elif command.startswith("move "):
                    # Команда: move <motor> <percentage>
                    parts = command.split()
                    if len(parts) == 3:
                        try:
                            motor = int(parts[1])
                            percentage = float(parts[2])
                            await robot.move_to_percentage(motor, percentage)
                        except ValueError:
                            print("Usage: move <motor> <percentage> (0.0-1.0)")
                    else:
                        print("Usage: move <motor> <percentage>")
                elif command.startswith("position "):
                    # Команда: position <name>
                    parts = command.split()
                    if len(parts) == 2:
                        position_name = parts[1]
                        await robot.move_to_position(position_name)
                    else:
                        print("Usage: position <name>")
                elif command.startswith("smooth "):
                    # Команда: smooth <motor> <start> <end>
                    parts = command.split()
                    if len(parts) == 4:
                        try:
                            motor = int(parts[1])
                            start = float(parts[2])
                            end = float(parts[3])
                            await robot.smooth_move(motor, start, end)
                        except ValueError:
                            print("Usage: smooth <motor> <start> <end>")
                    else:
                        print("Usage: smooth <motor> <start> <end>")
                else:
                    print("Unknown command")
                    
            except KeyboardInterrupt:
                print("\nInterrupted by user")
                break
            except Exception as e:
                print(f"Error: {e}")
        
        return True
        
    except Exception as e:
        print(f"Interactive mode failed: {e}")
        return False
    finally:
        await robot.disconnect()

async def main():
    """Основная функция"""
    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        await interactive_calibrated_mode()
    else:
        await demo_calibrated_movements()

if __name__ == "__main__":
    asyncio.run(main())
