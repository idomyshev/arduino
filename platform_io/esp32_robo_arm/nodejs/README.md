# ESP32 Robot Arm BLE Controller (TypeScript)

Контроллер для управления робо-рукой ESP32 через Bluetooth Low Energy на Node.js/TypeScript.

## Установка

```bash
# Перейти в директорию
cd nodejs

# Установить зависимости
yarn install

# Собрать проект
yarn build
```

## Использование

### Поиск устройства ESP32

```bash
yarn scan
# или
node dist/robot.js scan
```

Выполняет поиск устройства ESP32-RobotArm в течение 10 секунд.

### Подключение и интерактивный режим

```bash
yarn connect
# или
node dist/robot.js connect
```

Подключается к устройству и открывает интерактивную консоль для управления.

**Интерактивные команды:**

- `m <motor> <direction> <speed> [duration]` - Управление мотором
  - `motor`: 0, 1, 2 (M1, M2, M3)
  - `direction`: forward, backward
  - `speed`: 0-255
  - `duration`: время работы в миллисекундах (опционально)

- `stop` - Остановить все моторы
- `help` - Показать справку
- `quit` - Выход

**Примеры команд:**

```bash
# M1 вперед с скоростью 150
m 0 forward 150

# M2 назад с скоростью 100 на 2 секунды
m 1 backward 100 2000

# M3 вперед на максимальной скорости на 1.5 секунды
m 2 forward 255 1500
```

### Демонстрационная последовательность

```bash
yarn demo
# или
node dist/robot.js demo
```

Выполняет демонстрационную последовательность движений робо-руки.

## Использование в коде

```typescript
import { RobotArmController } from './classes/RobotArmController';

async function example() {
  const controller = new RobotArmController();
  
  // Поиск устройства
  const device = await controller.scanForDevice();
  
  // Подключение
  if (device) {
    if (await controller.connect(device.id)) {
      
      // Отправка команд
      await controller.sendCommand(0, 'forward', 150, 2000);
      
      // Остановка всех моторов
      await controller.stopAllMotors();
      
      // Отключение
      await controller.disconnect();
    }
  }
}
```

## API

### Класс RobotArmController

#### Методы

- `scanForDevice(timeout?: number): Promise<BLEDevice | null>` - Поиск устройства ESP32
- `connect(deviceId: string): Promise<boolean>` - Подключение к устройству
- `disconnect(): Promise<void>` - Отключение от устройства
- `sendCommand(motor: number, direction: string, speed: number, duration?: number): Promise<boolean>` - Отправка команды управления мотором
- `stopAllMotors(): Promise<void>` - Остановка всех моторов
- `demoSequence(): Promise<void>` - Выполнение демонстрационной последовательности
- `isConnected(): boolean` - Проверка состояния подключения

## Требования

- Node.js 18+
- macOS с включенным Bluetooth
- ESP32 с прошивкой робота
- Noble BLE библиотека (@abandonware/noble)

## Разработка

```bash
# Сборка проекта
yarn build

# Запуск в режиме разработки
yarn dev

# Запуск конкретной команды
yarn scan      # Поиск устройства
yarn connect   # Подключение и интерактивный режим
yarn demo      # Демо последовательность
yarn example   # Запуск примера
```

## Совместимость

Эта TypeScript версия полностью совместима с Python версией `robot_arm_controller.py` и использует те же BLE настройки:

- **SERVICE_UUID**: `12345678-1234-1234-1234-123456789abc`
- **CHARACTERISTIC_UUID**: `87654321-4321-4321-4321-cba987654321`
- **DEVICE_NAME**: `ESP32-RobotArm`

## Лицензия

MIT

