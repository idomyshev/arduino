# Enhanced Motor Calibration with API Storage

Улучшенная система калибровки моторов робота-руки с сохранением данных через API в базу данных.

## 🚀 Возможности

### ✅ **Множественные режимы хранения**
- **API только** - данные сохраняются только на сервер
- **Файл только** - данные сохраняются только локально (совместимость)
- **Гибридный** - данные сохраняются и на сервер, и локально

### ✅ **Автоматическая синхронизация**
- Загрузка существующих данных при запуске
- Сохранение результатов калибровки в реальном времени
- Резервное копирование в случае сбоя API

### ✅ **Улучшенный интерфейс**
- Интерактивное меню выбора режима
- Тест подключения к API
- Статус калибровки в реальном времени

## 📁 Файлы системы

```
python/
├── enhanced_calibrate.py          # Основной класс калибровки с API
├── quick_calibrate.py             # Быстрый запуск калибровки
├── test_calibration_api.py       # Тест API подключения
└── classes/
    └── data_storage_manager.py    # Менеджер хранения данных
```

## 🛠 Установка и запуск

### 1. Убедитесь, что сервер запущен
```bash
cd python/server
python3 data_server.py
```

### 2. Запуск калибровки

#### **Быстрый тест API:**
```bash
python3 test_calibration_api.py
```

#### **Интерактивная калибровка:**
```bash
python3 enhanced_calibrate.py
```

#### **Быстрый запуск:**
```bash
python3 quick_calibrate.py
```

## 🎯 Режимы работы

### **1. API Only (Рекомендуется)**
```python
calibrator = EnhancedMotorCalibrator(
    robot_id="esp32_robot_arm_001",
    server_url="http://localhost:8000/api",
    use_api=True,
    fallback_to_file=False
)
```

**Преимущества:**
- ✅ Централизованное хранение
- ✅ Синхронизация между устройствами
- ✅ История калибровок
- ✅ Веб-интерфейс для мониторинга

### **2. File Only (Совместимость)**
```python
calibrator = EnhancedMotorCalibrator(
    use_api=False,
    fallback_to_file=True
)
```

**Преимущества:**
- ✅ Работает без интернета
- ✅ Совместимость со старым кодом
- ✅ Быстрый доступ

### **3. Hybrid (Лучший вариант)**
```python
calibrator = EnhancedMotorCalibrator(
    robot_id="esp32_robot_arm_001",
    server_url="http://localhost:8000/api",
    use_api=True,
    fallback_to_file=True
)
```

**Преимущества:**
- ✅ Работает офлайн и онлайн
- ✅ Автоматическое резервное копирование
- ✅ Синхронизация при подключении к интернету

## 🔧 Процесс калибровки

### **Интерактивная калибровка:**

1. **Выбор робота** - введите ID робота
2. **Выбор режима хранения** - API/файл/гибридный
3. **Подключение к ESP32** - автоматическое сканирование
4. **Загрузка данных** - существующие калибровки
5. **Выбор мотора** - калибровка всех или конкретного
6. **Процесс калибровки:**
   - Движение к минимальной позиции (forward)
   - Движение к максимальной позиции (backward)  
   - Возврат к минимальной позиции (return)
7. **Сохранение результатов** - в API и/или файл

### **Автоматическая калибровка:**
```python
# Калибровка всех моторов
await calibrator.calibrate_all_motors(speed=150)

# Калибровка одного мотора
await calibrator.calibrate_motor(motor=0, speed=150)
```

## 📊 Структура данных калибровки

### **В API (MotorCalibrationData):**
```json
{
  "motor_id": 0,
  "calibrated": true,
  "calibration_date": "2025-01-14T12:00:00",
  "forward_time": 9.2,
  "backward_time": 14.4,
  "speed": 150,
  "min_position": null,
  "max_position": null,
  "return_time": 3.8,
  "total_travel_time": 23.6,
  "average_travel_time": 11.8
}
```

### **В файле (совместимость):**
```json
{
  "0": {
    "calibrated": true,
    "calibration_date": "2025-01-14T12:00:00",
    "forward_time": 9.2,
    "backward_time": 14.4,
    "speed": 150,
    "positions": {
      "min": null,
      "max": null
    },
    "return_time": 3.8,
    "total_travel_time": 23.6,
    "average_travel_time": 11.8
  }
}
```

## 🌐 API эндпоинты для калибровки

### **Сохранение калибровки:**
```bash
curl -X POST http://localhost:8000/api/calibration \
  -H "Content-Type: application/json" \
  -d '{
    "robot_id": "esp32_robot_arm_001",
    "calibration_data": {
      "0": {
        "motor_id": 0,
        "calibrated": true,
        "calibration_date": "2025-01-14T12:00:00",
        "forward_time": 9.2,
        "backward_time": 14.4,
        "speed": 150
      }
    }
  }'
```

### **Получение калибровки:**
```bash
curl http://localhost:8000/api/calibration/esp32_robot_arm_001
```

## 🔄 Миграция с существующей системы

### **Старый способ:**
```python
from classes.motor_calibration import MotorCalibrator

calibrator = MotorCalibrator()
await calibrator.interactive_calibration()
```

### **Новый способ:**
```python
from enhanced_calibrate import EnhancedMotorCalibrator

calibrator = EnhancedMotorCalibrator(
    robot_id="esp32_robot_arm_001",
    use_api=True,
    fallback_to_file=True
)
await calibrator.interactive_calibration()
```

**Все существующие методы работают без изменений!**

## 🐛 Отладка

### **Проверка API:**
```python
calibrator = EnhancedMotorCalibrator()
await calibrator.test_api_connection()
```

### **Проверка данных:**
```python
await calibrator.load_calibration_data()
calibrator.show_calibration_status()
```

### **Логи сервера:**
```bash
# Запуск с подробными логами
uvicorn data_server:app --host 0.0.0.0 --port 8000 --log-level debug
```

## 📈 Преимущества новой системы

### **По сравнению со старой системой:**

| Функция | Старая система | Новая система |
|---------|----------------|---------------|
| Хранение | Только файлы | API + файлы + БД |
| Синхронизация | Нет | Автоматическая |
| История | Нет | Полная история |
| Мониторинг | Нет | Веб-интерфейс |
| Резервирование | Нет | Автоматическое |
| Масштабируемость | Ограниченная | Высокая |

### **Практические преимущества:**

1. **Надежность** - данные не теряются при сбоях
2. **Совместная работа** - несколько человек могут калибровать
3. **Аналитика** - статистика калибровок и производительности
4. **Удаленное управление** - калибровка через веб-интерфейс
5. **Автоматизация** - интеграция с CI/CD системами

## 🚀 Примеры использования

### **Быстрая калибровка одного мотора:**
```python
calibrator = EnhancedMotorCalibrator(use_api=True)
await calibrator.connect()
await calibrator.calibrate_motor(0, speed=150)
await calibrator.save_calibration_data()
await calibrator.disconnect()
```

### **Калибровка с проверкой API:**
```python
calibrator = EnhancedMotorCalibrator()

# Проверяем API
if await calibrator.test_api_connection():
    calibrator.use_api = True
    print("Using API storage")
else:
    calibrator.use_api = False
    print("Using file storage")

await calibrator.interactive_calibration()
```

### **Программная калибровка:**
```python
calibrator = EnhancedMotorCalibrator(robot_id="robot_001")

await calibrator.connect()
await calibrator.load_calibration_data()

# Калибруем только неоткалиброванные моторы
for motor in range(3):
    if not calibrator.calibration_data.get(motor, {}).get("calibrated"):
        await calibrator.calibrate_motor(motor, speed=150)

await calibrator.save_calibration_data()
await calibrator.disconnect()
```

---

**Теперь калибровка моторов стала намного надежнее и удобнее! 🤖✨**
