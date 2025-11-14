#!/usr/bin/env node
/**
 * ESP32 Robot Arm BLE Controller (TypeScript)
 * Управление робо-рукой ESP32 через Bluetooth Low Energy
 */

// CLI интерфейс
import readline from 'readline';
import { RobotArmController } from './classes/RobotArmController.js';

/**
 * Вывод справки по командам
 */
function printHelp(): void {
  console.log(`
ESP32 Robot Arm BLE Controller

Команды:
  node dist/robot.js scan          - Поиск устройства
  node dist/robot.js connect      - Подключение и интерактивный режим
  node dist/robot.js demo         - Демонстрационная последовательность
  
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

  return new Promise<void>((resolve) => {
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
      resolve();
      process.exit(0);
    });
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
  }
}

// Запуск
if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch(console.error);
}

