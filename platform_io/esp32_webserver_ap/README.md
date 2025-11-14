# ESP32 WebServer Control LED

Проект для управления светодиодом и сервоприводом через веб-сервер на ESP32.

## Описание

ESP32 создает точку доступа WiFi и запускает веб-сервер для управления:
- Встроенным светодиодом (GPIO 2)
- Сервоприводом (GPIO 18)

## Структура проекта

```
esp32_webserver_control_led/
├── platformio.ini      # Configuration file for PlatformIO
├── src/
│   └── main.cpp       # Main source code
└── README.md          # This file
```

## Требования

- PlatformIO Core или PlatformIO IDE
- ESP32 DevKit
- Сервопривод (подключен к GPIO 18)

## Установка зависимостей

PlatformIO автоматически установит все необходимые библиотеки при первой сборке:
- ESP32Servo - для управления сервоприводом

## Сборка и загрузка

```bash
# Build the project
pio run

# Upload to ESP32
pio run --target upload

# Open serial monitor
pio device monitor
```

## Настройка WiFi

По умолчанию:
- SSID: `ESP32-AP`
- Password: `Angara86**`
- IP Address: `192.168.4.1`

Эти параметры можно изменить в файле `src/main.cpp`.

## API команды

Отправляйте HTTP GET запросы на ESP32:
- `GET /on?XXX` - включить LED и установить позицию сервопривода (0-180)
- `GET /of` - выключить LED

## Лицензия

MIT

