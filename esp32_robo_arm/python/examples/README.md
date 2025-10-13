# Robot Arm Examples

Папка содержит примеры использования робо-руки ESP32, включая интерактивные контроллеры и демонстрационные скрипты.

## Структура

```
examples/
├── interactive_calibrated.py    # Интерактивный контроллер с калибровкой
├── simple_interactive.py        # Простой интерактивный контроллер
├── example_calibrated.py        # Пример использования CalibratedRobotArm
├── test_duration.py            # Тест функциональности duration
└── README.md                   # Этот файл
```

## Интерактивные контроллеры

### 🤖 Interactive Calibrated Robot Arm Controller

**Файл:** `interactive_calibrated.py`

**Описание:** Полнофункциональный интерактивный контроллер робо-руки с использованием данных калибровки. Демонстрирует все возможности исправленного класса `CalibratedRobotArm`.

**Запуск:**

```bash
python python/examples/interactive_calibrated.py
```

**Основные возможности:**

- 🔌 Подключение/отключение к ESP32
- 🎯 Управление моторами с точным позиционированием
- 📍 Предустановленные позиции (home, pick, place, rest, extended, retracted)
- 🔄 Плавные движения между позициями
- 🎬 Демонстрационные последовательности (pickplace, wave)
- 📊 Информация о статусе калибровки и текущих позициях
- ❓ Встроенная справка по командам

**Команды:**

```bash
# Базовое управление
move <мотор> <позиция>    # Движение в позицию (0-100%)
set <мотор> <позиция>     # То же что move
stop <мотор>              # Остановить мотор
stopall                   # Остановить все моторы

# Предустановленные позиции
home|pick|place|rest|extended|retracted

# Плавные движения
smooth <мотор> <от> <до> [шаги]

# Демонстрации
pickplace|wave

# Информация
status|positions|available|reset

# Управление
connect|disconnect|help|exit
```

**Особенности:**

- ✅ Умное позиционирование - проверка текущей позиции перед движением
- ✅ Автоматическое направление - направление рассчитывается автоматически
- ✅ Отслеживание позиций - система знает текущие позиции всех моторов
- ✅ Гибкое управление - поддержка процентов и десятичных значений

### 🎮 Simple Interactive Controller

**Файл:** `simple_interactive.py`

**Описание:** Упрощенный интерактивный контроллер для базового управления робо-рукой.

**Запуск:**

```bash
python python/examples/simple_interactive.py
```

**Основные возможности:**

- Простое управление моторами
- Отслеживание позиций
- Проверка текущей позиции перед движением
- Автоматическое определение направления движения

## Демонстрационные скрипты

### 📚 Example Calibrated Robot Arm

**Файл:** `example_calibrated.py`

**Описание:** Пример использования класса `CalibratedRobotArm` в демонстрационном и интерактивном режимах.

**Запуск:**

```bash
python python/examples/example_calibrated.py
```

**Режимы:**

- **Демонстрационный** - автоматическое выполнение последовательностей
- **Интерактивный** - ручное управление с помощью команд

### ⏱️ Test Duration

**Файл:** `test_duration.py`

**Описание:** Тест функциональности параметра `duration` для автоматической остановки моторов.

**Запуск:**

```bash
python python/examples/test_duration.py
```

**Что тестирует:**

- Отправку команды с параметром `duration`
- Автоматическую остановку моторов по истечении времени
- Корректность работы ESP32 с временными ограничениями

## Быстрый старт

### 1. Интерактивный контроллер с калибровкой

```bash
# Запуск
python python/examples/interactive_calibrated.py

# Подключение
🤖 Введите команду: connect

# Проверка статуса
🤖 Введите команду: status

# Управление
🤖 Введите команду: move 0 50
```

### 2. Простой интерактивный контроллер

```bash
# Запуск
python python/examples/simple_interactive.py

# Управление
🤖 Введите команду: set 0 100
```

### 3. Демонстрационный режим

```bash
# Запуск
python python/examples/example_calibrated.py

# Выбор режима
1 - Демонстрационный режим
2 - Интерактивный режим
```

## Создание новых примеров

1. Скопируйте шаблон из существующего файла
2. Импортируйте необходимые классы:
   ```python
   from classes.calibrated_robot_arm import CalibratedRobotArm
   from classes.robot_arm_controller import RobotArmController
   ```
3. Создайте свою логику
4. Добавьте описание в этот README

### Шаблон нового примера:

```python
#!/usr/bin/env python3
"""
Example: Description
"""

import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from classes.calibrated_robot_arm import CalibratedRobotArm

async def main():
    """Главная функция"""
    robot = CalibratedRobotArm()

    try:
        if await robot.connect():
            # Ваш код здесь
            pass
    finally:
        await robot.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
```
