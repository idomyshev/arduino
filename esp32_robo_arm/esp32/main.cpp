// ESP32 Robot Arm — BLE управление через JSON команды, ESP32 core 3.x API

#include <Arduino.h>
#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>
#include <ArduinoJson.h>

// BLE настройки
// Эти UUID сгенерированы случайно для примера, их можно заменить на любые другие уникальные значения.
// Главное — чтобы они совпадали на стороне ESP32 и клиента (например, Python-скрипта).
#define SERVICE_UUID "12345678-1234-1234-1234-123456789abc"
#define CHARACTERISTIC_UUID "87654321-4321-4321-4321-cba987654321"

// Пины для моторов
#define M1_PWM 18 // PWM выход на PWMA (базовый поворот)
#define M1_IN1 16 // AIN1
#define M1_IN2 17 // AIN2

#define M2_PWM 19 // PWM выход на PWMB (подъем/опускание)
#define M2_IN1 21 // BIN1
#define M2_IN2 22 // BIN2

#define M3_PWM 23 // PWM выход на PWMC (сгибание/разгибание)
#define M3_IN1 25 // CIN1
#define M3_IN2 26 // CIN2

#define STBY 27 // STBY (держать HIGH)

#define PWM_FREQ 20000 // 20 кГц — плавная работа сервоприводов
#define PWM_BITS 8     // 0..255 диапазон duty

// Состояние моторов
struct MotorState
{
    int speed;               // Скорость 0-255
    bool forward;            // Направление: true = вперед, false = назад
    unsigned long startTime; // Время начала работы мотора
    unsigned long duration;  // Длительность работы в миллисекундах (0 = бесконечно)
    bool hasDuration;        // Есть ли ограничение по времени
};

MotorState motors[3] = {
    {0, true, 0, 0, false}, // M1
    {0, true, 0, 0, false}, // M2
    {0, true, 0, 0, false}  // M3
};

// Forward declarations
void processCommand(String jsonCommand);
void updateMotors();
void stopAllMotors();

// BLE переменные
BLEServer *pServer = NULL;
BLECharacteristic *pCharacteristic = NULL;
bool deviceConnected = false;
bool oldDeviceConnected = false;

// Класс для обработки BLE событий
class MyServerCallbacks : public BLEServerCallbacks
{
    void onConnect(BLEServer *pServer)
    {
        deviceConnected = true;
        Serial.println("Device connected");
    };

    void onDisconnect(BLEServer *pServer)
    {
        deviceConnected = false;
        Serial.println("Device disconnected");
        // Останавливаем все моторы при отключении
        stopAllMotors();
    }
};

// Класс для обработки команд
class MyCallbacks : public BLECharacteristicCallbacks
{
    void onWrite(BLECharacteristic *pCharacteristic)
    {
        std::string rxValue = pCharacteristic->getValue();

        if (rxValue.length() > 0)
        {
            Serial.println("Received command: " + String(rxValue.c_str()));
            processCommand(String(rxValue.c_str()));
        }
    }
};

void setup()
{
    Serial.begin(115200);
    Serial.println("Starting ESP32 Robot Arm BLE Server...");

    // Настройка пинов моторов
    pinMode(M1_IN1, OUTPUT);
    pinMode(M1_IN2, OUTPUT);
    pinMode(M2_IN1, OUTPUT);
    pinMode(M2_IN2, OUTPUT);
    pinMode(M3_IN1, OUTPUT);
    pinMode(M3_IN2, OUTPUT);
    pinMode(STBY, OUTPUT);

    digitalWrite(STBY, HIGH); // включаем драйвер

    // Настройка PWM каналов для ESP32 Arduino framework 3.x
    ledcSetup(0, PWM_FREQ, PWM_BITS); // канал 0 для M1
    ledcSetup(1, PWM_FREQ, PWM_BITS); // канал 1 для M2
    ledcSetup(2, PWM_FREQ, PWM_BITS); // канал 2 для M3

    ledcAttachPin(M1_PWM, 0); // привязываем пин к каналу
    ledcAttachPin(M2_PWM, 1);
    ledcAttachPin(M3_PWM, 2);

    // Инициализация BLE
    BLEDevice::init("ESP32-RobotArm");
    pServer = BLEDevice::createServer();
    pServer->setCallbacks(new MyServerCallbacks());

    BLEService *pService = pServer->createService(SERVICE_UUID);

    pCharacteristic = pService->createCharacteristic(
        CHARACTERISTIC_UUID,
        BLECharacteristic::PROPERTY_READ |
            BLECharacteristic::PROPERTY_WRITE);

    pCharacteristic->setCallbacks(new MyCallbacks());
    pCharacteristic->setValue("Robot Arm Ready");

    pService->start();

    BLEAdvertising *pAdvertising = BLEDevice::getAdvertising();
    pAdvertising->addServiceUUID(SERVICE_UUID);
    pAdvertising->setScanResponse(false);
    pAdvertising->setMinPreferred(0x0);
    BLEDevice::startAdvertising();

    Serial.println("Waiting for BLE connection...");
}

void loop()
{
    // Обработка подключения/отключения BLE
    if (!deviceConnected && oldDeviceConnected)
    {
        delay(500);                  // даем время для завершения отключения
        pServer->startAdvertising(); // перезапускаем рекламу
        Serial.println("Start advertising");
        oldDeviceConnected = deviceConnected;
    }

    if (deviceConnected && !oldDeviceConnected)
    {
        oldDeviceConnected = deviceConnected;
    }

    // Обновляем состояние моторов
    updateMotors();

    delay(50); // Небольшая задержка для стабильности
}

// Обработка JSON команд
void processCommand(String jsonCommand)
{
    JsonDocument doc;
    DeserializationError error = deserializeJson(doc, jsonCommand);

    if (error)
    {
        Serial.println("JSON parsing failed: " + String(error.c_str()));
        return;
    }

    // Проверяем наличие обязательных полей
    if (!doc["motor"].is<int>() || !doc["direction"].is<String>() || !doc["speed"].is<int>())
    {
        Serial.println("Invalid command format");
        return;
    }

    int motorIndex = doc["motor"];       // 0, 1, 2 для M1, M2, M3
    String direction = doc["direction"]; // "forward" или "backward"
    int speed = doc["speed"];            // 0-255
    unsigned long duration = 0;          // Длительность в миллисекундах (0 = бесконечно)
    bool hasDuration = false;            // Есть ли ограничение по времени

    // Проверяем наличие опционального параметра duration
    if (doc["duration"].is<unsigned long>())
    {
        duration = doc["duration"];
        hasDuration = true;
    }

    // Проверяем корректность параметров
    if (motorIndex < 0 || motorIndex > 2)
    {
        Serial.println("Invalid motor index: " + String(motorIndex));
        return;
    }

    if (speed < 0 || speed > 255)
    {
        Serial.println("Invalid speed: " + String(speed));
        return;
    }

    // Обновляем состояние мотора
    motors[motorIndex].speed = speed;
    motors[motorIndex].forward = (direction == "forward");
    motors[motorIndex].hasDuration = hasDuration;
    motors[motorIndex].duration = duration;
    motors[motorIndex].startTime = millis(); // Записываем время начала работы

    String logMessage = "Motor " + String(motorIndex) +
                        " set to " + direction +
                        " speed " + String(speed);

    if (hasDuration)
    {
        logMessage += " for " + String(duration) + "ms";
    }

    Serial.println(logMessage);
}

// Обновление состояния всех моторов
void updateMotors()
{
    unsigned long currentTime = millis();

    for (int i = 0; i < 3; i++)
    {
        // Проверяем, не истекло ли время работы мотора
        if (motors[i].hasDuration && motors[i].speed > 0)
        {
            if (currentTime - motors[i].startTime >= motors[i].duration)
            {
                // Время истекло, останавливаем мотор
                motors[i].speed = 0;
                motors[i].hasDuration = false;
                Serial.println("Motor " + String(i) + " stopped after " + String(motors[i].duration) + "ms");
            }
        }

        // Устанавливаем скорость
        ledcWrite(i, motors[i].speed);

        // Устанавливаем направление только если мотор работает
        if (motors[i].speed > 0)
        {
            if (motors[i].forward)
            {
                // Вращение вперед
                if (i == 0)
                { // M1
                    digitalWrite(M1_IN1, HIGH);
                    digitalWrite(M1_IN2, LOW);
                }
                else if (i == 1)
                { // M2
                    digitalWrite(M2_IN1, HIGH);
                    digitalWrite(M2_IN2, LOW);
                }
                else if (i == 2)
                { // M3
                    digitalWrite(M3_IN1, HIGH);
                    digitalWrite(M3_IN2, LOW);
                }
            }
            else
            {
                // Вращение назад
                if (i == 0)
                { // M1
                    digitalWrite(M1_IN1, LOW);
                    digitalWrite(M1_IN2, HIGH);
                }
                else if (i == 1)
                { // M2
                    digitalWrite(M2_IN1, LOW);
                    digitalWrite(M2_IN2, HIGH);
                }
                else if (i == 2)
                { // M3
                    digitalWrite(M3_IN1, LOW);
                    digitalWrite(M3_IN2, HIGH);
                }
            }
        }
        else
        {
            // Мотор остановлен - устанавливаем все пины в LOW
            if (i == 0)
            { // M1
                digitalWrite(M1_IN1, LOW);
                digitalWrite(M1_IN2, LOW);
            }
            else if (i == 1)
            { // M2
                digitalWrite(M2_IN1, LOW);
                digitalWrite(M2_IN2, LOW);
            }
            else if (i == 2)
            { // M3
                digitalWrite(M3_IN1, LOW);
                digitalWrite(M3_IN2, LOW);
            }
        }
    }
}

// Остановка всех моторов
void stopAllMotors()
{
    for (int i = 0; i < 3; i++)
    {
        motors[i].speed = 0;
        motors[i].hasDuration = false;
        motors[i].duration = 0;
    }
    Serial.println("All motors stopped");
}