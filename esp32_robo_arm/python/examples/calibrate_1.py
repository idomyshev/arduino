#!/usr/bin/env python3
"""
Calibrate 1: Demo Sequence for CalibratedRobotArm
Демонстрационная последовательность из 10 команд для класса CalibratedRobotArm
Показывает различные возможности точного позиционирования и калибровки
"""

import asyncio
import sys
import os

# Добавляем родительскую папку в путь для импорта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from classes.calibrated_robot_arm import CalibratedRobotArm

class Calibrate1Demo:
    """Демонстрационная последовательность для CalibratedRobotArm"""
    
    def __init__(self):
        self.robot = CalibratedRobotArm()
        self.command_delay = 10  # Задержка между командами в секундах
    
    async def run_demo(self):
        """Запуск демонстрационной последовательности"""
        print("=" * 70)
        print("🤖 CALIBRATE 1: ДЕМОНСТРАЦИОННАЯ ПОСЛЕДОВАТЕЛЬНОСТЬ")
        print("=" * 70)
        print("📋 Последовательность из 10 команд с задержкой 10 секунд")
        print("🎯 Демонстрирует возможности класса CalibratedRobotArm")
        print("=" * 70)
        
        try:
            # Подключение к ESP32
            print("\n🔌 Подключение к ESP32...")
            if not await self.robot.connect():
                print("❌ Ошибка подключения! Убедитесь что ESP32 включен и в зоне доступа.")
                return False
            
            print("✅ Подключение успешно!")
            
            # Показываем статус калибровки
            print("\n📊 Статус калибровки моторов:")
            self.robot.show_calibration_status()
            
            # Последовательность команд
            commands = [
                {
                    "name": "Домашняя позиция",
                    "description": "Переход всех моторов в позицию 0% (домашняя позиция)",
                    "action": lambda: self.robot.move_to_position("home")
                },
                {
                    "name": "Движение мотора 0 в 50%",
                    "description": "Точное позиционирование мотора 0 в середину диапазона",
                    "action": lambda: self.robot.move_to_percentage(0, 0.5)
                },
                {
                    "name": "Движение мотора 1 в 75%",
                    "description": "Позиционирование мотора 1 в 75% от максимального положения",
                    "action": lambda: self.robot.move_to_percentage(1, 0.75)
                },
                {
                    "name": "Движение мотора 2 в 25%",
                    "description": "Позиционирование мотора 2 в 25% от максимального положения",
                    "action": lambda: self.robot.move_to_percentage(2, 0.25)
                },
                {
                    "name": "Позиция захвата",
                    "description": "Переход в предустановленную позицию 'pick' (30%, 70%, 50%)",
                    "action": lambda: self.robot.move_to_position("pick")
                },
                {
                    "name": "Плавное движение мотора 0",
                    "description": "Плавное движение мотора 0 от текущей позиции до 100% (10 шагов)",
                    "action": lambda: self.robot.smooth_move(0, self.robot.get_current_position(0), 1.0, 10)
                },
                {
                    "name": "Позиция размещения",
                    "description": "Переход в предустановленную позицию 'place' (80%, 40%, 20%)",
                    "action": lambda: self.robot.move_to_position("place")
                },
                {
                    "name": "Плавное движение мотора 1",
                    "description": "Плавное движение мотора 1 от текущей позиции до 0% (15 шагов)",
                    "action": lambda: self.robot.smooth_move(1, self.robot.get_current_position(1), 0.0, 15)
                },
                {
                    "name": "Максимально вытянутая позиция",
                    "description": "Переход в позицию 'extended' (100%, 100%, 100%)",
                    "action": lambda: self.robot.move_to_position("extended")
                },
                {
                    "name": "Возврат в домашнюю позицию",
                    "description": "Финальный переход в позицию 'home' (0%, 0%, 0%)",
                    "action": lambda: self.robot.move_to_position("home")
                }
            ]
            
            # Выполняем команды
            for i, command in enumerate(commands, 1):
                print(f"\n{'='*70}")
                print(f"🎯 КОМАНДА {i}/10: {command['name']}")
                print(f"📝 Описание: {command['description']}")
                print(f"⏱️  Выполнение через {self.command_delay} секунд...")
                print(f"{'='*70}")
                
                # Обратный отсчет
                for countdown in range(self.command_delay, 0, -1):
                    print(f"⏰ {countdown}...", end="\r")
                    await asyncio.sleep(1)
                
                print(f"\n🚀 Выполняем: {command['name']}")
                
                try:
                    # Выполняем команду
                    await command['action']()
                    print(f"✅ Команда {i} выполнена успешно!")
                    
                    # Показываем текущие позиции
                    print("\n📊 Текущие позиции моторов:")
                    self.robot.show_current_positions()
                    
                except Exception as e:
                    print(f"❌ Ошибка выполнения команды {i}: {e}")
                
                # Пауза между командами (кроме последней)
                if i < len(commands):
                    print(f"\n⏸️  Пауза 3 секунды перед следующей командой...")
                    await asyncio.sleep(3)
            
            print(f"\n{'='*70}")
            print("🎉 ДЕМОНСТРАЦИОННАЯ ПОСЛЕДОВАТЕЛЬНОСТЬ ЗАВЕРШЕНА!")
            print("✅ Все 10 команд выполнены успешно")
            print("🤖 Робо-рука вернулась в домашнюю позицию")
            print(f"{'='*70}")
            
            return True
            
        except Exception as e:
            print(f"❌ Критическая ошибка: {e}")
            return False
        
        finally:
            # Отключаемся
            if self.robot.connected:
                print("\n🔌 Отключение от ESP32...")
                await self.robot.disconnect()
                print("✅ Отключение выполнено")
    
    async def run_interactive_mode(self):
        """Интерактивный режим - пользователь выбирает команды"""
        print("=" * 70)
        print("🎮 ИНТЕРАКТИВНЫЙ РЕЖИМ CALIBRATE 1")
        print("=" * 70)
        print("📋 Доступные команды:")
        
        commands = [
            ("1", "Домашняя позиция", "home"),
            ("2", "Движение мотора 0 в 50%", "move_0_50"),
            ("3", "Движение мотора 1 в 75%", "move_1_75"),
            ("4", "Движение мотора 2 в 25%", "move_2_25"),
            ("5", "Позиция захвата", "pick"),
            ("6", "Плавное движение мотора 0", "smooth_0"),
            ("7", "Позиция размещения", "place"),
            ("8", "Плавное движение мотора 1", "smooth_1"),
            ("9", "Максимально вытянутая позиция", "extended"),
            ("10", "Возврат в домашнюю позицию", "home"),
            ("all", "Выполнить все команды последовательно", "all"),
            ("status", "Показать статус калибровки", "status"),
            ("positions", "Показать текущие позиции", "positions"),
            ("exit", "Выход", "exit")
        ]
        
        for cmd_id, name, _ in commands:
            print(f"  {cmd_id:4} - {name}")
        
        print("=" * 70)
        
        try:
            if not await self.robot.connect():
                print("❌ Ошибка подключения!")
                return False
            
            while True:
                try:
                    choice = input("\n🎯 Выберите команду (или 'exit' для выхода): ").strip().lower()
                    
                    if choice == "exit":
                        break
                    elif choice == "all":
                        await self.run_demo()
                        break
                    elif choice == "status":
                        self.robot.show_calibration_status()
                    elif choice == "positions":
                        self.robot.show_current_positions()
                    elif choice == "1" or choice == "home":
                        await self.robot.move_to_position("home")
                        print("✅ Переход в домашнюю позицию")
                    elif choice == "2" or choice == "move_0_50":
                        await self.robot.move_to_percentage(0, 0.5)
                        print("✅ Мотор 0 установлен в позицию 50%")
                    elif choice == "3" or choice == "move_1_75":
                        await self.robot.move_to_percentage(1, 0.75)
                        print("✅ Мотор 1 установлен в позицию 75%")
                    elif choice == "4" or choice == "move_2_25":
                        await self.robot.move_to_percentage(2, 0.25)
                        print("✅ Мотор 2 установлен в позицию 25%")
                    elif choice == "5" or choice == "pick":
                        await self.robot.move_to_position("pick")
                        print("✅ Переход в позицию захвата")
                    elif choice == "6" or choice == "smooth_0":
                        current_pos = self.robot.get_current_position(0)
                        await self.robot.smooth_move(0, current_pos, 1.0, 10)
                        print("✅ Плавное движение мотора 0 до 100%")
                    elif choice == "7" or choice == "place":
                        await self.robot.move_to_position("place")
                        print("✅ Переход в позицию размещения")
                    elif choice == "8" or choice == "smooth_1":
                        current_pos = self.robot.get_current_position(1)
                        await self.robot.smooth_move(1, current_pos, 0.0, 15)
                        print("✅ Плавное движение мотора 1 до 0%")
                    elif choice == "9" or choice == "extended":
                        await self.robot.move_to_position("extended")
                        print("✅ Переход в максимально вытянутую позицию")
                    elif choice == "10":
                        await self.robot.move_to_position("home")
                        print("✅ Возврат в домашнюю позицию")
                    else:
                        print("❌ Неизвестная команда. Попробуйте снова.")
                    
                    # Показываем текущие позиции после каждой команды
                    print("\n📊 Текущие позиции:")
                    self.robot.show_current_positions()
                    
                except ValueError:
                    print("❌ Неверный формат команды")
                except Exception as e:
                    print(f"❌ Ошибка выполнения команды: {e}")
            
        except KeyboardInterrupt:
            print("\n\n👋 Программа прервана пользователем")
        except EOFError:
            print("\n\n👋 Выход из программы")
        finally:
            if self.robot.connected:
                await self.robot.disconnect()

async def main():
    """Главная функция"""
    demo = Calibrate1Demo()
    
    print("🤖 CALIBRATE 1: Демонстрация CalibratedRobotArm")
    print("=" * 50)
    print("Выберите режим:")
    print("1 - Автоматическая демонстрация (10 команд)")
    print("2 - Интерактивный режим")
    print("=" * 50)
    
    try:
        choice = input("Введите номер режима (1 или 2): ").strip()
        
        if choice == "1":
            await demo.run_demo()
        elif choice == "2":
            await demo.run_interactive_mode()
        else:
            print("❌ Неверный выбор. Запускаем автоматическую демонстрацию...")
            await demo.run_demo()
            
    except KeyboardInterrupt:
        print("\n\n👋 Программа прервана пользователем")
    except EOFError:
        print("\n\n👋 Выход из программы")

if __name__ == "__main__":
    asyncio.run(main())
