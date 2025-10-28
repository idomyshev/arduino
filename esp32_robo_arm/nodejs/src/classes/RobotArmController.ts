
import noble from '@abandonware/noble';

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

// BLE настройки (должны совпадать с ESP32)
const SERVICE_UUID = '12345678-1234-1234-1234-123456789abc';
const CHARACTERISTIC_UUID = '87654321-4321-4321-4321-cba987654321';
const DEVICE_NAME = 'ESP32-RobotArm';

export class RobotArmController     {
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
  