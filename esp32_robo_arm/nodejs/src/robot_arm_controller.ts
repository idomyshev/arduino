#!/usr/bin/env node
/**
 * ESP32 Robot Arm BLE Controller (TypeScript)
 * Управление робо-рукой ESP32 через Bluetooth Low Energy
 */

import noble from '@abandonware/noble';

// BLE настройки (должны совпадать с ESP32)
const SERVICE_UUID = '12345678-1234-1234-1234-123456789abc';
const CHARACTERISTIC_UUID = '87654321-4321-4321-4321-cba987654321';
const DEVICE_NAME = 'ESP32-RobotArm';

interface BLEDevice {
  id: string;
  name: string;
  address: string;
}

interface MotorCommand {
  motor: number;
  direction: string;
  speed: number;
  duration?: number;
}

export class RobotArmController {
  private peripheral: noble.Peripheral | null = null;
  private characteristic: any | null = null;
  private connected: boolean = false;

  /**
   * Поиск устройства ESP32-RobotArm
   */
  async scanForDevice(timeout: number = 10000): Promise<BLEDevice | null> {
    console.log('Scanning for ESP32 Robot Arm...');

    return new Promise((resolve, reject) => {
      let found = false;

      const scanComplete = () => {
        noble.removeListener('discover', onDiscover);
        if (!found) {
          console.log('Device not found!');
          resolve(null);
        }
      };

      const onDiscover = async (peripheral: noble.Peripheral) => {
        const name = peripheral.advertisement.localName;
        
        if (name && name.includes(DEVICE_NAME)) {
          found = true;
          console.log(`Found device: ${name} (${peripheral.address})`);
          noble.stopScanning();
          
          resolve({
            id: peripheral.id,
            name: name,
            address: peripheral.address
          });
        }
      };

      noble.on('discover', onDiscover);

      // Начинаем сканирование
      const startScanning = () => {
        noble.startScanning([], false);
      };

      // Проверяем текущее состояние
      const currentState = (noble as any)._state || 'unknown';
      if (currentState === 'poweredOn') {
        startScanning();
      } else {
        noble.on('stateChange', (state: string) => {
          if (state === 'poweredOn') {
            startScanning();
          }
        });
      }

      setTimeout(scanComplete, timeout);
    });
  }

  /**
   * Подключение к устройству
   */
  async connect(deviceId: string): Promise<boolean> {
    try {
      const peripheral = await this.getPeripheralById(deviceId);
      
      if (!peripheral) {
        console.log('Device not found!');
        return false;
      }

      this.peripheral = peripheral;

      // Подключаемся
      await peripheral.connectAsync();

      const name = peripheral.advertisement?.localName || 'Unknown';
      console.log(`Connected to ${name}`);

      // Получаем сервисы
      const { services } = await this.getServices(peripheral);
      const targetService = services.find(s => s.uuid.toLowerCase() === SERVICE_UUID.toLowerCase().replace(/-/g, ''));

      if (!targetService) {
        console.log('Service not found!');
        await peripheral.disconnectAsync();
        return false;
      }

      // Получаем характеристику
      const { characteristics } = await this.getCharacteristics(targetService);
      const targetCharacteristic = characteristics.find(
        c => c.uuid.toLowerCase() === CHARACTERISTIC_UUID.toLowerCase().replace(/-/g, '')
      );

      if (!targetCharacteristic) {
        console.log('Characteristic not found!');
        await peripheral.disconnectAsync();
        return false;
      }

      this.characteristic = targetCharacteristic;
      this.connected = true;
      return true;
    } catch (error) {
      console.log(`Connection failed: ${error}`);
      return false;
    }
  }

  /**
   * Отключение от устройства
   */
  async disconnect(): Promise<void> {
    if (this.peripheral && this.connected) {
      try {
        await this.peripheral.disconnectAsync();
      } catch (error) {
        // Игнорируем ошибки отключения
      }
      this.connected = false;
      console.log('Disconnected');
    }
  }

  /**
   * Отправка команды управления мотором
   * 
   * @param motor - номер мотора (0, 1, 2 для M1, M2, M3)
   * @param direction - направление ("forward" или "backward")
   * @param speed - скорость (0-255)
   * @param duration - время работы в миллисекундах (опционально)
   */
  async sendCommand(motor: number, direction: string, speed: number, duration?: number): Promise<boolean> {
    if (!this.connected || !this.characteristic) {
      console.log('Not connected to device!');
      return false;
    }

    // Создаем JSON команду
    const command: MotorCommand = {
      motor: motor,
      direction: direction,
      speed: speed
    };

    // Добавляем duration если указан
    if (duration !== undefined) {
      command.duration = duration;
    }

    const jsonCommand = JSON.stringify(command);
    console.log(`Sending command: ${jsonCommand}`);

    try {
      const buffer = Buffer.from(jsonCommand);
      await (this.characteristic as any).writeAsync(buffer, false);
      return true;
    } catch (error) {
      console.log(`Failed to send command: ${error}`);
      return false;
    }
  }

  /**
   * Остановка всех моторов
   */
  async stopAllMotors(): Promise<void> {
    console.log('Stopping all motors...');
    for (let motor = 0; motor < 3; motor++) {
      await this.sendCommand(motor, 'forward', 0);
    }
  }

  /**
   * Демонстрационная последовательность движений
   */
  async demoSequence(): Promise<void> {
    console.log('Starting demo sequence...');

    // Демо: поочередное движение моторов с автоматической остановкой
    for (let motor = 0; motor < 3; motor++) {
      console.log(`Moving motor ${motor} forward for 2 seconds...`);
      await this.sendCommand(motor, 'forward', 150, 2000);
      await this.sleep(2500); // Ждем немного больше времени работы

      console.log(`Moving motor ${motor} backward for 1.5 seconds...`);
      await this.sendCommand(motor, 'backward', 150, 1500);
      await this.sleep(2000); // Ждем завершения работы

      console.log(`Motor ${motor} should have stopped automatically`);
      await this.sleep(500);
    }

    // Демо: синхронное движение всех моторов с разным временем
    console.log('Synchronized movement with different durations...');
    await this.sendCommand(0, 'forward', 100, 3000);  // 3 секунды
    await this.sendCommand(1, 'backward', 100, 2000);  // 2 секунды
    await this.sendCommand(2, 'forward', 100, 1500);  // 1.5 секунды
    await this.sleep(3500); // Ждем завершения всех движений

    await this.stopAllMotors();
    console.log('Demo completed!');
  }

  /**
   * Проверка подключения
   */
  isConnected(): boolean {
    return this.connected;
  }

  /**
   * Сон на указанное количество миллисекунд
   */
  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Получение периферийного устройства по ID
   */
  private async getPeripheralById(id: string): Promise<noble.Peripheral | null> {
    return new Promise((resolve, reject) => {
      const onDiscover = (peripheral: noble.Peripheral) => {
        if (peripheral.id === id) {
          noble.removeListener('discover', onDiscover);
          noble.stopScanning();
          resolve(peripheral);
        }
      };

      noble.on('discover', onDiscover);

      // Начинаем сканирование
      const startScanning = () => {
        noble.startScanning([], false);
      };

      // Проверяем текущее состояние
      const currentState = (noble as any)._state || 'unknown';
      if (currentState === 'poweredOn') {
        startScanning();
      } else {
        noble.on('stateChange', (state: string) => {
          if (state === 'poweredOn') {
            startScanning();
          }
        });
      }

      // Timeout
      setTimeout(() => {
        noble.removeListener('discover', onDiscover);
        resolve(null);
      }, 10000);
    });
  }

  /**
   * Получение сервисов периферийного устройства
   */
  private async getServices(peripheral: noble.Peripheral): Promise<{ services: noble.Service[] }> {
    return new Promise((resolve, reject) => {
      peripheral.discoverServices([], (error, services) => {
        if (error) {
          reject(error);
        } else {
          resolve({ services });
        }
      });
    });
  }

  /**
   * Получение характеристик сервиса
   */
  private async getCharacteristics(service: noble.Service): Promise<{ characteristics: noble.Characteristic[] }> {
    return new Promise((resolve, reject) => {
      service.discoverCharacteristics([], (error, characteristics) => {
        if (error) {
          reject(error);
        } else {
          resolve({ characteristics });
        }
      });
    });
  }
}

// CLI интерфейс
import readline from 'readline';

/**
 * Вывод справки по командам
 */
function printHelp(): void {
  console.log(`
ESP32 Robot Arm BLE Controller

Команды:
  node dist/robot_arm_controller.js scan          - Поиск устройства
  node dist/robot_arm_controller.js connect      - Подключение и интерактивный режим
  node dist/robot_arm_controller.js demo         - Демонстрационная последовательность
  
Интерактивные команды (после подключения):
  m <motor> <direction> <speed> [duration]  - Управление мотором
                                   motor: 0, 1, 2 (M1, M2, M3)
                                   direction: forward, backward
                                   speed: 0-255
                                   duration: время работы в миллисекундах (опционально)
  stop                           - Остановить все моторы
  help                           - Показать справку
  quit                           - Выход

Примеры:
  m 0 forward 150               - M1 вперед со скоростью 150 (бесконечно)
  m 1 backward 100 2000         - M2 назад со скоростью 100 на 2 секунды
  m 2 forward 255 1500          - M3 вперед на максимальной скорости на 1.5 секунды
`);
}

/**
 * Интерактивный режим управления
 */
async function interactiveMode(controller: RobotArmController): Promise<void> {
  console.log("Interactive mode. Type 'help' for commands, 'quit' to exit.");

  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
    prompt: 'Robot> '
  });

  rl.prompt();

  rl.on('line', async (line: string) => {
    const command = line.trim().toLowerCase();

    if (command === 'quit') {
      rl.close();
      return;
    } else if (command === 'help') {
      printHelp();
      rl.prompt();
    } else if (command === 'stop') {
      await controller.stopAllMotors();
      rl.prompt();
    } else if (command.startsWith('m ')) {
      // Команда управления мотором: m <motor> <direction> <speed> [duration]
      const parts = command.split(' ');
      
      if (parts.length >= 4 && parts.length <= 5) {
        try {
          const motor = parseInt(parts[1]);
          const direction = parts[2];
          const speed = parseInt(parts[3]);
          let duration: number | undefined;

          // Проверяем наличие опционального параметра duration
          if (parts.length === 5) {
            duration = parseInt(parts[4]);
            if (duration <= 0) {
              console.log('Duration must be positive');
              rl.prompt();
              return;
            }
          }

          if (motor < 0 || motor > 2) {
            console.log('Motor must be 0, 1, or 2');
            rl.prompt();
            return;
          }

          if (direction !== 'forward' && direction !== 'backward') {
            console.log("Direction must be 'forward' or 'backward'");
            rl.prompt();
            return;
          }

          if (speed < 0 || speed > 255) {
            console.log('Speed must be 0-255');
            rl.prompt();
            return;
          }

          await controller.sendCommand(motor, direction, speed, duration);
        } catch (error) {
          console.log('Invalid motor, speed, or duration value');
        }
      } else {
        console.log('Usage: m <motor> <direction> <speed> [duration]');
      }
      
      rl.prompt();
    } else {
      console.log("Unknown command. Type 'help' for available commands.");
      rl.prompt();
    }
  });

  rl.on('close', () => {
    process.exit(0);
  });
}

/**
 * Основная функция
 */
async function main(): Promise<void> {
  const args = process.argv.slice(2);

  if (args.length < 1) {
    printHelp();
    return;
  }

  const command = args[0].toLowerCase();
  const controller = new RobotArmController();

  try {
    if (command === 'scan') {
      const device = await controller.scanForDevice();
      if (device) {
        console.log(`Device found: ${device.name} at ${device.address}`);
      }
    } else if (command === 'connect') {
      const device = await controller.scanForDevice();
      if (device) {
        if (await controller.connect(device.id)) {
          await interactiveMode(controller);
        }
      }
    } else if (command === 'demo') {
      const device = await controller.scanForDevice();
      if (device) {
        if (await controller.connect(device.id)) {
          await controller.demoSequence();
        }
      }
    } else {
      console.log("Unknown command. Use 'scan', 'connect', or 'demo'");
    }
  } catch (error) {
    console.log(`Error: ${error}`);
  } finally {
    await controller.disconnect();
    process.exit(0);
  }
}

// Запуск
if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch(console.error);
}

