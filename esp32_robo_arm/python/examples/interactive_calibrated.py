#!/usr/bin/env python3
"""
Interactive Calibrated Robot Arm Controller
Интерактивный контроллер робо-руки с использованием данных калибровки
Демонстрирует все возможности класса CalibratedRobotArm
"""

import asyncio
import sys
import os

# Добавляем родительскую папку в путь для импорта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from classes.calibrated_robot_arm import CalibratedRobotArm

class InteractiveCalibratedRobotArm:
    """Интерактивный контроллер робо-руки с калибровкой"""
    
    def __init__(self):
        self.robot = CalibratedRobotArm()
        self.running = False
    
    def print_help(self):
        """Показать справку по командам"""
        print(f"\n{'='*60}")
        print("🤖 ИНТЕРАКТИВНЫЙ КОНТРОЛЛЕР РОБО-РУКИ")
        print(f"{'='*60}")
        print("📋 ДОСТУПНЫЕ КОМАНДЫ:")
        print()
        print("🔌 ПОДКЛЮЧЕНИЕ:")
        print("  connect     - Подключиться к ESP32")
        print("  disconnect  - Отключиться от ESP32")
        print()
        print("🎯 УПРАВЛЕНИЕ МОТОРАМИ:")
        print("  move <мотор> <позиция>  - Движение мотора в позицию (0-100%)")
        print("  set <мотор> <позиция>  - То же что move")
        print("  stop <мотор>           - Остановить мотор")
        print("  stopall                - Остановить все моторы")
        print()
        print("📍 ПРЕДУСТАНОВЛЕННЫЕ ПОЗИЦИИ:")
        print("  home       - Домашняя позиция (0%, 0%, 0%)")
        print("  pick       - Позиция захвата (30%, 70%, 50%)")
        print("  place      - Позиция размещения (80%, 40%, 20%)")
        print("  rest       - Позиция отдыха (10%, 10%, 10%)")
        print("  extended   - Максимально вытянутая (100%, 100%, 100%)")
        print("  retracted  - Максимально втянутая (0%, 0%, 0%)")
        print()
        print("🔄 ПЛАВНЫЕ ДВИЖЕНИЯ:")
        print("  smooth <мотор> <от> <до> [шаги] - Плавное движение между позициями")
        print()
        print("🎬 ДЕМОНСТРАЦИОННЫЕ ПОСЛЕДОВАТЕЛЬНОСТИ:")
        print("  pickplace   - Последовательность: взять → переместить → положить")
        print("  wave        - Последовательность: махание рукой")
        print()
        print("📊 ИНФОРМАЦИЯ:")
        print("  status      - Показать статус калибровки")
        print("  positions   - Показать текущие позиции моторов")
        print("  available   - Показать доступные предустановленные позиции")
        print("  reset       - Сбросить отслеживание позиций")
        print()
        print("❓ СПРАВКА:")
        print("  help        - Показать эту справку")
        print("  exit        - Выход из программы")
        print()
        print("💡 ПРИМЕРЫ:")
        print("  move 0 50     - Движение мотора 0 в позицию 50%")
        print("  set 1 100      - Установка мотора 1 в позицию 100%")
        print("  smooth 0 0 100 - Плавное движение мотора 0 от 0% до 100%")
        print("  pickplace      - Запуск демонстрационной последовательности")
        print(f"{'='*60}")
    
    async def handle_command(self, command: str):
        """Обработка команд пользователя"""
        parts = command.strip().lower().split()
        if not parts:
            return
        
        cmd = parts[0]
        
        try:
            if cmd == "help":
                self.print_help()
            
            elif cmd == "connect":
                if await self.robot.connect():
                    print("✅ Подключение успешно!")
                    self.robot.show_calibration_status()
                else:
                    print("❌ Ошибка подключения!")
            
            elif cmd == "disconnect":
                await self.robot.disconnect()
                print("✅ Отключение выполнено!")
            
            elif cmd in ["move", "set"]:
                if len(parts) != 3:
                    print("❌ Неверный формат: move <мотор> <позиция>")
                    print("   Пример: move 0 50")
                    return
                
                motor = int(parts[1])
                position = float(parts[2])
                
                # Если позиция больше 1, считаем что это проценты (0-100)
                if position > 1:
                    position = position / 100.0
                
                if position < 0 or position > 1:
                    print("❌ Позиция должна быть от 0 до 100%")
                    return
                
                await self.robot.move_to_percentage(motor, position)
                print(f"✅ Мотор {motor} установлен в позицию {position*100:.1f}%")
            
            elif cmd == "stop":
                if len(parts) != 2:
                    print("❌ Неверный формат: stop <мотор>")
                    return
                
                motor = int(parts[1])
                await self.robot.controller.send_command(motor, "forward", 0)
                print(f"✅ Мотор {motor} остановлен")
            
            elif cmd == "stopall":
                await self.robot.controller.stop_all_motors()
                print("✅ Все моторы остановлены")
            
            elif cmd in ["home", "pick", "place", "rest", "extended", "retracted"]:
                await self.robot.move_to_position(cmd)
                print(f"✅ Переход в позицию '{cmd}' выполнен")
            
            elif cmd == "smooth":
                if len(parts) < 4:
                    print("❌ Неверный формат: smooth <мотор> <от> <до> [шаги]")
                    return
                
                motor = int(parts[1])
                start_pos = float(parts[2])
                end_pos = float(parts[3])
                steps = int(parts[4]) if len(parts) > 4 else 10
                
                # Конвертируем проценты в десятичные
                if start_pos > 1:
                    start_pos = start_pos / 100.0
                if end_pos > 1:
                    end_pos = end_pos / 100.0
                
                await self.robot.smooth_move(motor, start_pos, end_pos, steps)
                print(f"✅ Плавное движение мотора {motor} от {start_pos*100:.1f}% до {end_pos*100:.1f}%")
            
            elif cmd == "pickplace":
                await self.robot.pick_and_place_sequence()
                print("✅ Последовательность 'pick and place' завершена")
            
            elif cmd == "wave":
                await self.robot.wave_sequence()
                print("✅ Последовательность 'wave' завершена")
            
            elif cmd == "status":
                self.robot.show_calibration_status()
            
            elif cmd == "positions":
                self.robot.show_current_positions()
            
            elif cmd == "available":
                self.robot.show_available_positions()
            
            elif cmd == "reset":
                self.robot.reset_positions()
                print("✅ Отслеживание позиций сброшено")
            
            elif cmd == "exit":
                self.running = False
                print("👋 До свидания!")
            
            else:
                print(f"❌ Неизвестная команда: {cmd}")
                print("   Введите 'help' для справки")
        
        except ValueError as e:
            print(f"❌ Ошибка ввода: {e}")
        except Exception as e:
            print(f"❌ Ошибка выполнения команды: {e}")
    
    async def run(self):
        """Запуск интерактивного режима"""
        print("🤖 Интерактивный контроллер робо-руки запущен!")
        print("   Введите 'help' для справки по командам")
        print("   Введите 'exit' для выхода")
        
        self.running = True
        
        while self.running:
            try:
                command = input("\n🤖 Введите команду: ").strip()
                if command:
                    await self.handle_command(command)
            except KeyboardInterrupt:
                print("\n\n👋 Программа прервана пользователем")
                break
            except EOFError:
                print("\n\n👋 Выход из программы")
                break
        
        # Отключаемся при выходе
        if self.robot.connected:
            await self.robot.disconnect()

async def main():
    """Главная функция"""
    controller = InteractiveCalibratedRobotArm()
    await controller.run()

if __name__ == "__main__":
    asyncio.run(main())
