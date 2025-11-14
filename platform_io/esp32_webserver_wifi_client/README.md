# ESP32 WebServer Control LED

Проект для управления светодиодом и сервоприводом через веб-сервер на ESP32.

## Описание

ESP32 подключается к WiFi (iPhone hotspot или домашняя сеть) и запускает веб-сервер для управления:

- Встроенным светодиодом (GPIO 2)
- Сервоприводом (GPIO 18)

**Идеально работает с iPhone Personal Hotspot!**

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

### Вариант 1: iPhone Personal Hotspot (рекомендуется для мобильности)

1. **На iPhone:**

   - Настройки → Режим модема (Personal Hotspot)
   - Включите "Разрешать другим"
   - Запомните имя сети и пароль

2. **В коде (`src/main.cpp`):**

   ```cpp
   const char *ssid = "iPhone Ilia";      // Имя вашего iPhone hotspot
   const char *password = "12345678";     // Пароль hotspot
   ```

3. **Загрузите код на ESP32**

4. **На iPhone:**
   - Откройте Serial Monitor: `pio device monitor`
   - Скопируйте IP-адрес ESP32 (например: `172.20.10.2`)
   - Откройте Safari и введите: `http://172.20.10.2`

### Вариант 2: Домашний WiFi роутер

Просто измените `ssid` и `password` на данные вашей домашней сети в файле `src/main.cpp`.

## API команды

Отправляйте HTTP GET запросы на ESP32:

- `GET /on?XXX` - включить LED и установить позицию сервопривода (0-180)
- `GET /of` - выключить LED

## Лицензия

MIT
