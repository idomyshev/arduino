# Robot Arm Sequences

Папка содержит последовательности управления робо-рукой ESP32 и библиотеку команд.

## Структура

```
sequences/
├── robot_arm_library.py    # Библиотека команд для управления
├── algorithm_1.py          # Последовательность 1: Все моторы вперед 5с + поочередная остановка
└── README.md               # Этот файл
```

## Библиотека команд (robot_arm_library.py)

Удобная библиотека для создания последовательностей управления робо-рукой.

### Основные методы:

#### Подключение/отключение:

- `connect()` - подключение к ESP32
- `disconnect()` - отключение от ESP32

#### Управление моторами:

- `motor_forward(motor, speed, duration=None)` - мотор вперед
- `motor_backward(motor, speed, duration=None)` - мотор назад
- `motor_stop(motor)` - остановка конкретного мотора
- `all_motors_stop()` - остановка всех моторов

#### Групповые команды:

- `all_motors_forward(speed, duration=None)` - все моторы вперед
- `all_motors_backward(speed, duration=None)` - все моторы назад

#### Утилиты:

- `wait(seconds)` - пауза в секундах
- `motors_sequence(commands)` - выполнение последовательности команд

### Пример использования:

```python
from sequences.robot_arm_library import RobotArmLibrary

async def my_sequence():
    robot = RobotArmLibrary()

    await robot.connect()

    # Все моторы вперед на 3 секунды
    await robot.all_motors_forward(speed=150, duration=3000)
    await robot.wait(3.5)

    # Поочередная остановка
    for motor in range(3):
        await robot.motor_stop(motor)
        await robot.wait(2)

    await robot.disconnect()
```

## Последовательности

### Sequence 1: All Motors Forward 5s + Sequential Stop

**Описание:** Все три мотора работают вперед 5 секунд, затем поочередно останавливаются с паузами 5 секунд между остановками.

**Запуск:**

```bash
python sequences/algorithm_1.py
```

**Последовательность:**

1. Все моторы (0, 1, 2) вперед со скоростью 150 на 5 секунд
2. Пауза 5.5 секунд (ожидание завершения работы)
3. Остановка мотора 0
4. Пауза 5 секунд
5. Остановка мотора 1
6. Пауза 5 секунд
7. Остановка мотора 2

## Создание новых последовательностей

1. Скопируйте шаблон из `algorithm_1.py`
2. Импортируйте библиотеку: `from sequences.robot_arm_library import RobotArmLibrary`
3. Используйте методы библиотеки для создания последовательности команд
4. Добавьте описание в этот README

### Шаблон новой последовательности:

```python
#!/usr/bin/env python3
"""
Sequence X: Description
"""

import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sequences.robot_arm_library import RobotArmLibrary

async def sequence_x():
    """Описание последовательности"""
    print("=" * 50)
    print("Sequence X: Description")
    print("=" * 50)

    robot = RobotArmLibrary()

    try:
        if not await robot.connect():
            return False

        # Ваша последовательность здесь

        return True
    except Exception as e:
        print(f"Sequence failed: {e}")
        return False
    finally:
        await robot.disconnect()

if __name__ == "__main__":
    asyncio.run(sequence_x())
```
