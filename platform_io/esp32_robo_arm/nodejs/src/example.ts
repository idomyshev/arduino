/**
 * Пример использования RobotArmController
 */

import { RobotArmController } from './classes/RobotArmController.js';

async function main() {
  console.log('='.repeat(60));
  console.log('ESP32 Robot Arm Controller - Example');
  console.log('='.repeat(60));
  
  const controller = new RobotArmController();

  try {
    // Шаг 1: Поиск устройства
    console.log('\n1. Scanning for device...');
    const device = await controller.scanForDevice();
    
    if (!device) {
      console.log('❌ Device not found!');
      console.log('Make sure:');
      console.log('  - ESP32 is powered on');
      console.log('  - Bluetooth is enabled');
      console.log('  - Robot is in range');
      return;
    }
    
    console.log(`✅ Found: ${device.name} at ${device.address}`);
    
    // Шаг 2: Подключение
    console.log('\n2. Connecting to device...');
    const connected = await controller.connect(device.id);
    
    if (!connected) {
      console.log('❌ Failed to connect!');
      return;
    }
    
    console.log('✅ Connected successfully!');
    
    // Шаг 3: Управление моторами
    console.log('\n3. Testing motor control...');
    
    // Пример 1: Движение одного мотора
    console.log('Example 1: Motor 0 forward, speed 150, 2 seconds');
    await controller.sendCommand(0, 'forward', 150, 2000);
    await sleep(2500);
    
    // Пример 2: Движение назад
    console.log('Example 2: Motor 1 backward, speed 100, 1.5 seconds');
    await controller.sendCommand(1, 'backward', 100, 1500);
    await sleep(2000);
    
    // Пример 3: Синхронное движение всех моторов
    console.log('Example 3: Synchronized movement of all motors');
    await controller.sendCommand(0, 'forward', 120, 2000);
    await controller.sendCommand(1, 'backward', 120, 1500);
    await controller.sendCommand(2, 'forward', 120, 1000);
    await sleep(2500);
    
    // Шаг 4: Остановка
    console.log('\n4. Stopping all motors...');
    await controller.stopAllMotors();
    
    console.log('\n✅ Example completed successfully!');
    
  } catch (error) {
    console.error('❌ Error:', error);
  } finally {
    // Шаг 5: Отключение
    console.log('\n5. Disconnecting...');
    await controller.disconnect();
    console.log('✅ Disconnected');
  }
}

function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// Запуск примера
main().catch(console.error);

