# Enhanced Robot Arm Data Storage System

Улучшенная система хранения данных для робота-руки ESP32 с поддержкой сохранения калибровочных данных и текущих позиций.

## 🚀 Возможности

### ✅ Автоматическое сохранение позиций
- Позиции сохраняются автоматически при каждом движении
- Восстановление позиций при переподключении
- История движений робота

### ✅ Множественные источники хранения
- **Локальные файлы** - быстрый доступ, работа офлайн
- **Серверное API** - централизованное управление, синхронизация
- **SQLite база данных** - структурированное хранение, история
- **Гибридный режим** - лучшее из всех вариантов

### ✅ Совместимость
- Полная совместимость с существующим кодом
- Постепенная миграция на новую систему
- Поддержка старых файлов калибровки

## 📁 Структура файлов

```
python/
├── classes/
│   ├── data_storage_manager.py      # Универсальный менеджер хранения
│   ├── enhanced_calibrated_robot_arm.py  # Улучшенный контроллер
│   └── ... (существующие файлы)
├── server/
│   └── data_server.py               # Сервер для хранения данных
├── examples/
│   └── enhanced_example.py          # Пример использования
└── data/                            # Локальные данные (создается автоматически)
    ├── robot_data.json              # Калибровочные данные
    ├── robot_data_position.json     # Текущая позиция
    └── robot_data.db                # SQLite база данных
```

## 🛠 Установка зависимостей

```bash
cd python
pip install -r requirements.txt
```

Новые зависимости:
- `aiohttp` - для HTTP запросов к серверу
- `fastapi` - для создания API сервера
- `uvicorn` - ASGI сервер
- `pydantic` - валидация данных

## 🚀 Быстрый старт

### 1. Запуск сервера (опционально)

```bash
cd python/server
python data_server.py
```

Сервер будет доступен по адресу: `http://localhost:8000`

### 2. Использование улучшенного контроллера

```python
import asyncio
from classes.enhanced_calibrated_robot_arm import EnhancedCalibratedRobotArm, StorageType

async def main():
    # Создаем контроллер с гибридным хранением
    robot = EnhancedCalibratedRobotArm(
        robot_id="esp32_robot_arm_001",
        storage_type=StorageType.HYBRID,
        server_url="http://localhost:8000/api"
    )
    
    # Подключаемся (позиция загрузится автоматически)
    if await robot.connect():
        # Движения с автоматическим сохранением позиций
        await robot.move_to_position("home")
        await robot.move_to_position("pick")
        
        # Отключаемся (позиция сохранится автоматически)
        await robot.disconnect()

asyncio.run(main())
```

### 3. Запуск примера

```bash
# Полная демонстрация
python examples/enhanced_example.py

# Тест только системы хранения
python examples/enhanced_example.py storage
```

## 📊 Типы хранения данных

### 1. Локальные файлы (`StorageType.LOCAL_FILE`)
```python
robot = EnhancedCalibratedRobotArm(
    storage_type=StorageType.LOCAL_FILE
)
```
- ✅ Быстрый доступ
- ✅ Работа офлайн
- ❌ Нет синхронизации между устройствами

### 2. Серверное API (`StorageType.SERVER_API`)
```python
robot = EnhancedCalibratedRobotArm(
    storage_type=StorageType.SERVER_API,
    server_url="http://your-server.com/api"
)
```
- ✅ Централизованное управление
- ✅ Синхронизация между устройствами
- ❌ Требует интернет

### 3. База данных (`StorageType.DATABASE`)
```python
robot = EnhancedCalibratedRobotArm(
    storage_type=StorageType.DATABASE
)
```
- ✅ Структурированное хранение
- ✅ История движений
- ✅ Быстрые запросы

### 4. Гибридный режим (`StorageType.HYBRID`) - **Рекомендуется**
```python
robot = EnhancedCalibratedRobotArm(
    storage_type=StorageType.HYBRID,
    server_url="http://localhost:8000/api"
)
```
- ✅ Работает офлайн и онлайн
- ✅ Автоматическая синхронизация
- ✅ Резервное копирование

## 🔧 API сервера

### Эндпоинты

- `POST /api/calibration` - Сохранение калибровочных данных
- `GET /api/calibration/{robot_id}` - Получение калибровочных данных
- `POST /api/position` - Сохранение позиции
- `GET /api/position/{robot_id}` - Получение текущей позиции
- `GET /api/position/{robot_id}/history` - История позиций
- `GET /api/robots` - Список роботов
- `GET /api/status` - Статус сервера

### Пример запроса

```bash
# Получение калибровочных данных
curl http://localhost:8000/api/calibration/esp32_robot_arm_001

# Сохранение позиции
curl -X POST http://localhost:8000/api/position \
  -H "Content-Type: application/json" \
  -d '{
    "robot_id": "esp32_robot_arm_001",
    "position": {
      "timestamp": "2025-01-14T12:00:00",
      "motor_positions": {"0": 0.5, "1": 0.3, "2": 0.7},
      "position_name": "pick"
    }
  }'
```

## 🔄 Миграция с существующего кода

### Старый код:
```python
from classes.calibrated_robot_arm import CalibratedRobotArm

robot = CalibratedRobotArm()
await robot.connect()
await robot.move_to_position("home")
```

### Новый код:
```python
from classes.enhanced_calibrated_robot_arm import EnhancedCalibratedRobotArm, StorageType

robot = EnhancedCalibratedRobotArm(storage_type=StorageType.HYBRID)
await robot.connect()  # Позиция загрузится автоматически
await robot.move_to_position("home")  # Позиция сохранится автоматически
```

**Все существующие методы работают без изменений!**

## 📈 Преимущества новой системы

### 🎯 Решение проблемы "потерянной позиции"
- **Раньше**: При каждом запуске робот "забывал" где находится
- **Теперь**: Позиция сохраняется и восстанавливается автоматически

### 🔄 Синхронизация между устройствами
- Несколько компьютеров могут управлять одним роботом
- Данные синхронизируются автоматически

### 📊 Аналитика и мониторинг
- История всех движений робота
- Статистика использования
- Отслеживание производительности

### 🛡️ Надежность
- Резервное копирование данных
- Работа в офлайн режиме
- Автоматическое восстановление

## 🐛 Отладка

### Проверка сохранения данных
```python
# Проверяем историю позиций
history = await robot.get_position_history(limit=10)
for pos in history:
    print(f"{pos.timestamp}: {pos.position_name} - {pos.motor_positions}")

# Проверяем синхронизацию
sync_result = await robot.sync_data()
print(f"Sync successful: {sync_result}")
```

### Логи сервера
```bash
# Запуск сервера с подробными логами
uvicorn data_server:app --host 0.0.0.0 --port 8000 --log-level debug
```

## 🤝 Вклад в проект

1. Форкните репозиторий
2. Создайте ветку для новой функции
3. Внесите изменения
4. Создайте Pull Request

## 📝 Лицензия

MIT License - см. файл LICENSE для деталей.

## 🆘 Поддержка

При возникновении проблем:

1. Проверьте логи сервера
2. Убедитесь, что все зависимости установлены
3. Проверьте подключение к интернету (для серверного режима)
4. Создайте Issue в репозитории

---

**Теперь ваша робот-рука никогда не забудет, где она находится! 🤖✨**
