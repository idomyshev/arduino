# ESP32 Robot Arm - API-Only System

## Быстрый старт

### 1. Запуск API сервера
```bash
cd server
python3 data_server.py
```

### 2. Калибровка робота
```bash
python3 enhanced_calibrate.py
```

### 3. Использование робота
```bash
python3 api_only_example.py
```

## Основные файлы

- `enhanced_calibrate.py` - Калибровка робота
- `api_only_example.py` - Пример использования
- `final_api_test.py` - Тест системы
- `classes/calibrated_robot_arm.py` - Контроллер робота
- `server/data_server.py` - API сервер

## Требования

- Python 3.8+
- ESP32 с прошивкой робота
- Bluetooth включен
- API сервер запущен

## Установка зависимостей

```bash
pip3 install -r requirements.txt
```

## Тестирование

```bash
python3 final_api_test.py
```

Система работает только с API - никаких файлов! 🚀
