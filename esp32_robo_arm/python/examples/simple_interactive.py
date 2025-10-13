#!/usr/bin/env python3
"""
Simplified Interactive Robot Arm Control
Упрощенное интерактивное управление робо-рукой
"""

import asyncio
import sys
import os

# Добавляем родительскую папку в путь для импорта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from classes.calibrated_robot_arm import CalibratedRobotArm

class InteractiveRobotArm:
    """Упрощенный интерактивный контроллер робо-руки"""
    
    def __init__(self):
        self.robot = CalibratedRobotArm()
        self.connected = False
        self.current_positions = {0: 0.0, 1: 0.0, 2: 0.0}  # Текущие позиции моторов
    
    async def connect(self):
        """Подключение к ESP32"""
        if await self.robot.connect():
            self.connected = True
            print("✅ Подключено к ESP32 Robot Arm")
            self.robot.show_calibration_status()
            return True
        else:
            print("❌ Не удалось подключиться к ESP32")
            return False
    
    async def disconnect(self):
        """Отключение от ESP32"""
        if self.connected:
            await self.robot.disconnect()
            self.connected = False
            print("🔌 Отключено от ESP32")
    
    def show_help(self):
        """Показать справку по командам"""
        print("\n" + "="*60)
        print("🤖 ИНТЕРАКТИВНОЕ УПРАВЛЕНИЕ РОБО-РУКОЙ")
        print("="*60)
        print("\n📋 Доступные команды:")
        print("  set <мотор> <позиция>     - Установить мотор в позицию (0-100%)")
        print("  move <мотор> <позиция>    - То же что set")
        print("  home                      - Все моторы в домашнюю позицию (0%)")
        print("  pick                      - Переход в позицию захвата")
        print("  place                     - Переход в позицию размещения")
        print("  rest                      - Переход в позицию покоя")
        print("  status                    - Показать текущие позиции моторов")
        print("  calibrate                 - Показать статус калибровки")
        print("  positions                 - Показать доступные позиции")
        print("  reset                     - Сбросить отслеживание позиций")
        print("  help                      - Показать эту справку")
        print("  quit                      - Выход")
        print("\n💡 Примеры:")
        print("  set 0 50                  - Мотор 0 в позицию 50%")
        print("  move 1 25                 - Мотор 1 в позицию 25%")
        print("  set 2 100                 - Мотор 2 в максимальную позицию")
        print("  home                      - Все моторы в позицию 0%")
        print("\n🎯 Моторы: 0, 1, 2")
        print("📊 Позиции: 0% (минимум) - 100% (максимум)")
        print("="*60)
    
    def reset_positions(self):
        """Сбросить отслеживание позиций (использовать если позиции сбились)"""
        self.current_positions = {0: 0.0, 1: 0.0, 2: 0.0}
        print("🔄 Отслеживание позиций сброшено. Все моторы считаются в позиции 0%")
        print("⚠️  Внимание: Если моторы не в позиции 0%, используйте команду 'home' для синхронизации")
    
    def show_status(self):
        """Показать текущие позиции моторов"""
        print("\n📊 Текущие позиции моторов:")
        for motor, position in self.current_positions.items():
            print(f"  Мотор {motor}: {position*100:.1f}%")
        print()
    
    async def set_motor_position(self, motor: int, target_percentage: float):
        """Установить мотор в указанную позицию
        
        Args:
            motor: номер мотора (0, 1, 2)
            target_percentage: целевая позиция (0-100)
        """
        if not self.connected:
            print("❌ Не подключено к устройству!")
            return False
        
        if motor < 0 or motor > 2:
            print(f"❌ Неверный номер мотора: {motor}. Используйте 0, 1 или 2")
            return False
        
        if target_percentage < 0 or target_percentage > 100:
            print(f"❌ Неверная позиция: {target_percentage}%. Используйте 0-100")
            return False
        
        # Конвертируем проценты в десятичные (0-1)
        target_position = target_percentage / 100.0
        current_pos = self.current_positions[motor]
        
        # Проверяем, не находимся ли мы уже в целевой позиции
        position_tolerance = 0.02  # 2% толерантность
        if abs(target_position - current_pos) <= position_tolerance:
            print(f"✅ Мотор {motor} уже в позиции {target_percentage:.1f}% (текущая: {current_pos*100:.1f}%)")
            return True
        
        try:
            print(f"🎯 Мотор {motor}: {current_pos*100:.1f}% → {target_percentage:.1f}%")
            
            # Определяем направление движения
            if target_position > current_pos:
                direction = "→"  # Вперед (к максимальной позиции)
            elif target_position < current_pos:
                direction = "←"  # Назад (к минимальной позиции)
            else:
                direction = "="  # Уже в позиции
            
            print(f"   Направление: {direction}")
            
            # Выполняем движение
            await self.robot.move_to_percentage(motor, target_position)
            
            # Обновляем текущую позицию
            self.current_positions[motor] = target_position
            
            print(f"✅ Мотор {motor} установлен в позицию {target_percentage:.1f}%")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка при движении мотора {motor}: {e}")
            return False
    
    async def move_to_preset_position(self, position_name: str):
        """Переход в предустановленную позицию"""
        if not self.connected:
            print("❌ Не подключено к устройству!")
            return False
        
        try:
            print(f"🎯 Переход в позицию: {position_name}")
            await self.robot.move_to_position(position_name)
            
            # Обновляем текущие позиции (примерные значения)
            if position_name == "home":
                self.current_positions = {0: 0.0, 1: 0.0, 2: 0.0}
            elif position_name == "pick":
                self.current_positions = {0: 0.3, 1: 0.7, 2: 0.5}
            elif position_name == "place":
                self.current_positions = {0: 0.8, 1: 0.4, 2: 0.2}
            elif position_name == "rest":
                self.current_positions = {0: 0.1, 1: 0.1, 2: 0.1}
            elif position_name == "extended":
                self.current_positions = {0: 1.0, 1: 1.0, 2: 1.0}
            elif position_name == "retracted":
                self.current_positions = {0: 0.0, 1: 0.0, 2: 0.0}
            
            print(f"✅ Переход в позицию '{position_name}' завершен")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка при переходе в позицию '{position_name}': {e}")
            return False
    
    async def interactive_mode(self):
        """Основной интерактивный режим"""
        print("🤖 Запуск интерактивного управления робо-рукой...")
        
        if not await self.connect():
            return False
        
        self.show_help()
        
        try:
            while True:
                try:
                    command = input("\n🤖 Робот> ").strip()
                    
                    if not command:
                        continue
                    
                    parts = command.lower().split()
                    cmd = parts[0]
                    
                    if cmd == "quit" or cmd == "exit":
                        print("👋 До свидания!")
                        break
                    
                    elif cmd == "help":
                        self.show_help()
                    
                    elif cmd == "status":
                        self.show_status()
                    
                    elif cmd == "calibrate":
                        self.robot.show_calibration_status()
                    
                    elif cmd == "positions":
                        self.robot.show_available_positions()
                    
                    elif cmd == "reset":
                        self.reset_positions()
                    
                    elif cmd in ["set", "move"]:
                        if len(parts) == 3:
                            try:
                                motor = int(parts[1])
                                position = float(parts[2])
                                await self.set_motor_position(motor, position)
                            except ValueError:
                                print("❌ Неверный формат: set <мотор> <позиция>")
                                print("   Пример: set 0 50")
                        else:
                            print("❌ Неверный формат: set <мотор> <позиция>")
                            print("   Пример: set 0 50")
                    
                    elif cmd in ["home", "pick", "place", "rest", "extended", "retracted"]:
                        await self.move_to_preset_position(cmd)
                    
                    else:
                        print(f"❌ Неизвестная команда: {cmd}")
                        print("   Введите 'help' для справки")
                
                except KeyboardInterrupt:
                    print("\n⚠️ Прервано пользователем")
                    break
                except Exception as e:
                    print(f"❌ Ошибка: {e}")
            
            return True
            
        except Exception as e:
            print(f"❌ Интерактивный режим завершился с ошибкой: {e}")
            return False
        finally:
            await self.disconnect()

async def main():
    """Основная функция"""
    controller = InteractiveRobotArm()
    await controller.interactive_mode()

if __name__ == "__main__":
    asyncio.run(main())
