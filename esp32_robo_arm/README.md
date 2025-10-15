# ESP32 Robot Arm Control System

Современная система управления роботом-рукой на базе ESP32 с веб-интерфейсом на React.

## 📁 Структура проекта

```
esp32_robo_arm/
├── esp32/                    # Код для ESP32 микроконтроллера
│   ├── main.cpp             # Основной код ESP32
│   └── platformio.ini      # Конфигурация PlatformIO
├── python/                   # Python сервер и API
│   ├── server/
│   │   ├── data_server.py   # FastAPI сервер с WebSocket
│   │   └── robot_data_server.db
│   ├── classes/             # Классы для управления роботом
│   ├── examples/            # Примеры использования
│   └── tests/               # Тесты
└── robot-web-interface/     # React веб-интерфейс
    ├── src/
    │   ├── components/      # React компоненты
    │   ├── hooks/           # Custom hooks
    │   ├── services/        # WebSocket сервис
    │   └── types/           # TypeScript типы
    └── package.json
```

## 🚀 Быстрый старт

### 1. ESP32 микроконтроллер
```bash
cd esp32
# Установите PlatformIO и загрузите код на ESP32
pio run --target upload
```

### 2. Python сервер
```bash
cd python/server
pip install -r ../requirements.txt
python data_server.py
```

### 3. React веб-интерфейс
```bash
cd robot-web-interface
yarn install
yarn dev
```

## 🎮 Управление

- **Малое плечо (M1)**: Опустить/Поднять
- **Большое плечо (M2)**: Поднять/Опустить  
- **Клешня (M3)**: Закрыть/Открыть

## 🔧 Технологии

- **ESP32**: Bluetooth Low Energy (BLE)
- **Python**: FastAPI, WebSocket, SQLite
- **React**: TypeScript, Material-UI, Vite
- **Связь**: WebSocket между веб-интерфейсом и Python сервером

## 📡 Порты

- **Python сервер**: http://localhost:8000
- **React приложение**: http://localhost:5173
- **ESP32 BLE**: Автоматическое подключение

## 🎯 Особенности

- ✅ Современный веб-интерфейс с Material-UI
- ✅ Реальное время управления через WebSocket
- ✅ Автоматическое переподключение
- ✅ Темная тема интерфейса
- ✅ Адаптивный дизайн для мобильных устройств
- ✅ Типизация TypeScript для надежности
