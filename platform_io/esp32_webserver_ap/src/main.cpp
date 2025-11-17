#include <Arduino.h>
#include <WiFi.h>
#include <ESP32Servo.h>
#include <ArduinoJson.h>
#include <ESPAsyncWebServer.h>
#include <AsyncJson.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <Preferences.h>

Servo myServo;
int servoPin = 18;

// OLED Display configuration
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1 // Reset pin (not used)
#define SCREEN_ADDRESS 0x3C // I2C address for 0.96" OLED

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);
bool displayInitialized = false; // Флаг инициализации дисплея

// Preferences for permanent storage
Preferences preferences;

// Calibration state
struct CheckDirectionState {
    bool isActive;
    int motorNumber;
    bool isDirectionCorrect;
    unsigned long finishTime; // Time when calibration finished (for display)
} checkDirectionState = {false, -1, false, 0};

// Структура для пинов моторов
struct MotorPins
{
    int pwm;  // PWM выход
    int in1;  // IN1
    int in2;  // IN2
};

// Объект с пинами моторов
// I2C для OLED дисплея использует GPIO13 (SDA) и GPIO14 (SCL)
MotorPins motors[4] = {
    {18, 16, 17}, // M1 - базовый поворот
    {19, 21, 22}, // M2 - подъем/опускание
    {23, 25, 26}, // M3 - сгибание/разгибание
    {32, 33, 12}  // M4 - четвертый мотор
};

#define STBY 27 // STBY (держать HIGH)

#define PWM_FREQ 20000 // 20 кГц — плавная работа сервоприводов
#define PWM_BITS 8     // 0..255 диапазон duty

struct MotorState
{
    int speed;               // Скорость 0-255
    bool forward;            // Направление: true = вперед, false = назад
    unsigned long startTime; // Время начала работы мотора
    unsigned long duration;  // Длительность работы в миллисекундах (0 = бесконечно)
    bool hasDuration;        // Есть ли ограничение по времени
};

MotorState motorStates[4] = {
    {0, true, 0, 0, false}, // M1
    {0, true, 0, 0, false}, // M2
    {0, true, 0, 0, false}, // M3
    {0, true, 0, 0, false}  // M4
};

void processCommand(String jsonCommand);
void updateMotors();
void stopAllMotors();
void updateDisplay();
bool isMotorDirectionSet(int motor);
bool loadMotorDirection(int motor);
void saveMotorDirection(int motor, bool reverse);

// WiFi credentials - подключение к существующей сети
// Замените на имя и пароль вашей WiFi сети
const char *ssid = "DIGIFIBRA-6GDf";  // Имя вашей WiFi сети
const char *password = "XYbSCxGZsK";  // Пароль от WiFi сети

JsonDocument doc;
String jsonResponse;

// Set web server port number to 80
AsyncWebServer server(80);

// Variable to store the HTTP request
String header;

// On-board LED is connected to GPIO 2
const int ledPin = 2;

// Current state of the LED
String ledState = "OFF";

String command = "";
String speed = "";
String speedSign = "";

int speedInt = 0;

void setup()
{
    // Настройка пинов моторов
    for (int i = 0; i < 4; i++) {
        pinMode(motors[i].in1, OUTPUT);
        pinMode(motors[i].in2, OUTPUT);
    }
    pinMode(STBY, OUTPUT);

    digitalWrite(STBY, HIGH); // включаем драйвер

    // Настройка PWM каналов для ESP32 Arduino framework 3.x
    ledcSetup(0, PWM_FREQ, PWM_BITS); // канал 0 для M1
    ledcSetup(1, PWM_FREQ, PWM_BITS); // канал 1 для M2
    ledcSetup(2, PWM_FREQ, PWM_BITS); // канал 2 для M3
    ledcSetup(3, PWM_FREQ, PWM_BITS); // канал 3 для M4

    // Привязываем пины к каналам
    ledcAttachPin(motors[0].pwm, 0);
    ledcAttachPin(motors[1].pwm, 1);
    ledcAttachPin(motors[2].pwm, 2);
    ledcAttachPin(motors[3].pwm, 3);

    // myServo.attach(servoPin);
    // myServo.write(0);

    // Initialize the LED pin as an output
    pinMode(ledPin, OUTPUT);
    digitalWrite(ledPin, LOW); // LED is off initially

    // Start serial communication
    Serial.begin(115200);
    delay(1000);

    // Initialize Preferences for permanent storage
    preferences.begin("motors", false);

    // Initialize I2C and OLED display
    // Используем альтернативные пины для I2C: GPIO13 (SDA), GPIO14 (SCL)
    Wire.begin(13, 14); // SDA=GPIO13, SCL=GPIO14
    if (!display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS)) {
        Serial.println("SSD1306 allocation failed");
        displayInitialized = false;
        // Continue without display if initialization fails
    } else {
        Serial.println("OLED display initialized");
        displayInitialized = true;
        display.clearDisplay();
        display.setTextSize(1);
        display.setTextColor(SSD1306_WHITE);
        display.setCursor(0, 0);
        display.println("ESP32 Starting...");
        display.display();
    }

    // Connect to WiFi network
    Serial.print("Connecting to WiFi: ");
    Serial.println(ssid);
    
    WiFi.mode(WIFI_STA); // Устанавливаем режим станции (клиент)
    WiFi.begin(ssid, password);
    
    // Ожидание подключения
    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 30) {
        delay(500);
        Serial.print(".");
        attempts++;
    }
    
    if (WiFi.status() == WL_CONNECTED) {
        Serial.println("");
        Serial.println("WiFi connected!");
        Serial.print("IP Address: ");
        Serial.println(WiFi.localIP());
        
        // IP адрес будет отображаться в updateDisplay()
    } else {
        Serial.println("");
        Serial.println("Failed to connect to WiFi!");
        Serial.println("Please check SSID and password.");
        
        // Update OLED display with error
        display.clearDisplay();
        display.setCursor(0, 0);
        display.println("WiFi Failed!");
        display.println("Restarting...");
        display.display();
        
        Serial.println("Restarting in 5 seconds...");
        delay(5000);
        ESP.restart();
    }

        // Обработка POST запросов с JSON телом
        AsyncCallbackJsonWebHandler *handler = new AsyncCallbackJsonWebHandler("/run_motor", [](AsyncWebServerRequest *request, JsonVariant &json) {
            JsonObject jsonObj = json.as<JsonObject>();

            if (jsonObj["motor"].is<int>() && jsonObj["speed"].is<int>()) {
                int motor = jsonObj["motor"];
                int speed = jsonObj["speed"];
                // Проверяем наличие поля reverse (необязательное)
                bool inputReverse = jsonObj["reverse"].is<bool>() ? jsonObj["reverse"].as<bool>() : false;
                bool savedDirection = loadMotorDirection(motor);
                bool reverse = savedDirection ? inputReverse : !inputReverse;

                if (speed > 0) {
                    motorStates[motor].speed = speed;
                    motorStates[motor].forward = !reverse; // forward = true если не reverse
                    
                    ledcWrite(motor, speed);

                    if (reverse) {
                        digitalWrite(motors[motor].in1, LOW);
                        digitalWrite(motors[motor].in2, HIGH);
                    } else {
                        digitalWrite(motors[motor].in1, HIGH);
                        digitalWrite(motors[motor].in2, LOW);
                    }
                } else if (speed == 0) {
                    motorStates[motor].speed = 0;
                    ledcWrite(motor, 0);
                    digitalWrite(motors[motor].in1, LOW);
                    digitalWrite(motors[motor].in2, LOW);
                }
                
                updateDisplay();
            }
                
            AsyncJsonResponse *response = new AsyncJsonResponse();
            JsonObject root = response->getRoot();
            root["status"] = "ok";
            root["integrated_led_state"] = ledState;
            response->setLength();
            request->send(response);
        });

        handler->setMethod(HTTP_POST);
        
        server.addHandler(handler);
        
        AsyncCallbackJsonWebHandler *checkDirectionStartHandler = new AsyncCallbackJsonWebHandler("/check_direction_start", [](AsyncWebServerRequest *request, JsonVariant &json) {
            JsonObject jsonObj = json.as<JsonObject>();
            
            if (jsonObj["motor"].is<int>() && jsonObj["speed"].is<int>()) {
                int motor = jsonObj["motor"];
                int speed = jsonObj["speed"];
                
                checkDirectionState.isActive = true;
                checkDirectionState.motorNumber = motor;
                checkDirectionState.finishTime = 0;
                                
                motorStates[motor].speed = speed;
                motorStates[motor].forward = true;
                ledcWrite(motor, speed);
                digitalWrite(motors[motor].in1, HIGH);
                digitalWrite(motors[motor].in2, LOW);
                
                updateDisplay();
                
                AsyncJsonResponse *response = new AsyncJsonResponse();
                JsonObject root = response->getRoot();
                root["status"] = "ok";
                root["message"] = "Check direction started";
                root["motor"] = motor; 
                response->setLength();
                request->send(response);
            } else {
                request->send(400, "application/json", "{\"error\":\"Invalid parameters\"}");
            }
        });
        checkDirectionStartHandler->setMethod(HTTP_POST);
        server.addHandler(checkDirectionStartHandler);
        
        AsyncCallbackJsonWebHandler *checkDirectionStopHandler = new AsyncCallbackJsonWebHandler("/check_direction_stop", [](AsyncWebServerRequest *request, JsonVariant &json) {
            JsonObject jsonObj = json.as<JsonObject>();

            if (!checkDirectionState.isActive) {
                request->send(400, "application/json", "{\"error\":\"Checking direction was not run\"}");
                return;
            }
            
            if (jsonObj["is_direction_correct"].is<bool>()) {
                bool isDirectionCorrect = jsonObj["is_direction_correct"].as<bool>();
                int motor = checkDirectionState.motorNumber;
                
                // Stop motor
                motorStates[motor].speed = 0;
                ledcWrite(motor, 0);
                digitalWrite(motors[motor].in1, LOW);
                digitalWrite(motors[motor].in2, LOW);
                
                // Save calibration value
                saveMotorDirection(motor, isDirectionCorrect);
                checkDirectionState.isDirectionCorrect = isDirectionCorrect;
                checkDirectionState.finishTime = millis();
                                
                updateDisplay();
                
                AsyncJsonResponse *response = new AsyncJsonResponse();
                JsonObject root = response->getRoot();
                root["status"] = "ok";
                root["message"] = "Direction checking finished";
                root["motor"] = checkDirectionState.motorNumber;
                root["is_direction_correct"] = isDirectionCorrect;
                response->setLength();
                request->send(response);
            } else {
                request->send(400, "application/json", "{\"error\":\"Invalid parameters\"}");
            }
        });
        checkDirectionStopHandler->setMethod(HTTP_POST);
        server.addHandler(checkDirectionStopHandler);

        AsyncCallbackJsonWebHandler *checkDirectionStatusHandler = new AsyncCallbackJsonWebHandler("/check_direction_status", [](AsyncWebServerRequest *request, JsonVariant &json) {
            JsonObject jsonObj = json.as<JsonObject>();
            
            if (jsonObj["motor"].is<int>()) {
                int motor = jsonObj["motor"];

                bool isSavedDirection = isMotorDirectionSet(motor);
                
                updateDisplay();
                
                AsyncJsonResponse *response = new AsyncJsonResponse();
                JsonObject root = response->getRoot();
                root["status"] = "ok";
                root["message"] = "Check direction status";
                root["motor"] = motor; 

                if (!isSavedDirection) {
                    root["is_direction_correct"] = "undefined";
                } else {
                    root["is_direction_correct"] = loadMotorDirection(motor);
                }

                response->setLength();
                request->send(response);
            } else {
                request->send(400, "application/json", "{\"error\":\"Invalid parameters\"}");
            }
        });
        checkDirectionStatusHandler->setMethod(HTTP_POST);
        server.addHandler(checkDirectionStatusHandler);
        
        // Обработка 404
        server.onNotFound([](AsyncWebServerRequest *request) {
            request->send(404, "application/json", "{\"error\":\"Not found\"}");
        });

    // Start the server
    server.begin();
    
    // Первоначальное обновление дисплея
    updateDisplay();
}

// Функция для обновления OLED дисплея с информацией о моторах
void updateDisplay()
{
    // Проверяем, что дисплей инициализирован
    if (!displayInitialized) {
        return; // Если дисплей не инициализирован, выходим
    }
    
    display.clearDisplay();
    display.setTextSize(1);
    display.setTextColor(SSD1306_WHITE);
    
    // Первая строка: IP адрес
    display.setCursor(0, 0);
    if (WiFi.status() == WL_CONNECTED) {
        display.print("IP: ");
        display.println(WiFi.localIP());
    } else {
        display.println("WiFi disconnected");
    }
    
    // Вторая строка: пустая
    display.println();
    
    // С третьей строки: информация о калибровке или моторах
    if (checkDirectionState.isActive) {
        // Показываем "calibration started" на третьей строке
        display.println("Checking direction");
        display.print("for motor M");
        display.println(checkDirectionState.motorNumber + 1);
    } else if (checkDirectionState.finishTime > 0 && (millis() - checkDirectionState.finishTime) < 3000) {
        // Показываем результаты калибровки в течение 3 секунд
        display.println("Saved direction for motor M");
        display.println(checkDirectionState.motorNumber + 1);
        display.print("Direction was correct: ");
        display.println(checkDirectionState.isDirectionCorrect ? "true" : "false");
    } else {
        // Обычное отображение информации о моторах
        for (int i = 0; i < 4; i++) {
            display.print("M");
            display.print(i + 1);
            display.print(" ");
            // Если скорость равна 0, показываем "stop"
            if (motorStates[i].speed == 0) {
                display.println("stop");
            } else {
                // Форматируем скорость с ведущими пробелами (всегда 3 символа)
                char speedStr[4];
                sprintf(speedStr, "%3d", motorStates[i].speed);
                display.print(speedStr);
                display.print(" ");
                display.println(motorStates[i].forward ? "forward" : "reverse");
            }
        }
    }
    
    display.display();
}

bool loadMotorDirection(int motor) {
    String key = "m" + String(motor) + "_direction";
    return preferences.getBool(key.c_str(), true);
}

bool isMotorDirectionSet(int motor) {
    String key = "m" + String(motor) + "_direction";
    return preferences.isKey(key.c_str());
}

void saveMotorDirection(int motor, bool reverse) {
    String key = "m" + String(motor) + "_direction";
    preferences.putBool(key.c_str(), reverse);
}

void loop()
{
    // Check if calibration finished message should be cleared (after 3 seconds)
    if (checkDirectionState.finishTime > 0 && (millis() - checkDirectionState.finishTime) >= 3000) {
        checkDirectionState.isActive = false;
        checkDirectionState.motorNumber = -1;
        checkDirectionState.finishTime = 0;
        updateDisplay();
    }
}
