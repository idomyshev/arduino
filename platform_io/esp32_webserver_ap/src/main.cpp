#include <Arduino.h>
#include <WiFi.h>
#include <ESP32Servo.h>
#include <ArduinoJson.h>
#include <ESPAsyncWebServer.h>
#include <AsyncJson.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

Servo myServo;
int servoPin = 18;

// OLED Display configuration
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1 // Reset pin (not used)
#define SCREEN_ADDRESS 0x3C // I2C address for 0.96" OLED

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

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

    // Initialize I2C and OLED display
    // Используем альтернативные пины для I2C: GPIO13 (SDA), GPIO14 (SCL)
    Wire.begin(13, 14); // SDA=GPIO13, SCL=GPIO14
    if (!display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS)) {
        Serial.println("SSD1306 allocation failed");
        // Continue without display if initialization fails
    } else {
        Serial.println("OLED display initialized");
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
        
        // Update OLED display with WiFi info
        display.clearDisplay();
        display.setCursor(0, 0);
        display.println("WiFi Connected!");
        display.print("IP: ");
        display.println(WiFi.localIP());
        display.display();
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
        AsyncCallbackJsonWebHandler *handler = new AsyncCallbackJsonWebHandler("/", [](AsyncWebServerRequest *request, JsonVariant &json) {
            JsonObject jsonObj = json.as<JsonObject>();
            
            // Обработка JSON данных
            if (jsonObj["command"].is<String>())
            {
                String cmd = jsonObj["command"];
                Serial.println("Command: " + cmd);

                if (jsonObj["motor"].is<int>() && jsonObj["speed"].is<int>()) {
                    int motor = jsonObj["motor"];
                    int speed = jsonObj["speed"];
                    Serial.println("Motor: " + String(motor) + ", Speed: " + String(speed));
                    // Ваша логика управления моторами

                    if (cmd == "on") {
                        ledcWrite(motor, speed);
                        digitalWrite(motors[motor].in1, HIGH);
                        digitalWrite(motors[motor].in2, LOW);
                    } else if (cmd == "off") {
                        digitalWrite(motors[motor].in1, LOW);
                        digitalWrite(motors[motor].in2, LOW);
                    }
                }
                
                if (cmd == "on")
                {
                    digitalWrite(ledPin, HIGH);
                    ledState = "ON";
                }
                else if (cmd == "off")
                {
                    digitalWrite(ledPin, LOW);
                    ledState = "OFF";
                }
            }
            
            // Отправка JSON ответа
            AsyncJsonResponse *response = new AsyncJsonResponse();
            JsonObject root = response->getRoot();
            root["status"] = "ok";
            root["integrated_led_state"] = ledState;
            response->setLength();
            request->send(response);
        });

        handler->setMethod(HTTP_POST);
        
        server.addHandler(handler);
        
        // Обработка 404
        server.onNotFound([](AsyncWebServerRequest *request) {
            request->send(404, "application/json", "{\"error\":\"Not found\"}");
        });

    // Start the server
    server.begin();
}

void loop()
{
    // WiFiClient client = server.available(); // Listen for incoming clients

    // if (client)
    // { // If a new client connects
    //     // Serial.println("New Client.");          // Print a message in the serial monitor
    //     String currentLine = ""; // Make a String to hold incoming data from the client
    //     while (client.connected())
    //     { // Loop while the client is connected
    //         if (client.available())
    //         {                           // If there's bytes to read from the client,
    //             char c = client.read(); // Read a byte
    //             // Serial.write(c);                    // Print it out to the serial monitor
    //             header += c;
    //             if (c == '\n')
    //             { // If the byte is a newline character
    //                 if (currentLine.length() == 0)
    //                 {

               
    //                     // HTTP response
    //                     client.println("HTTP/1.1 200 OK");
    //                     client.println("Content-type:text/html");
    //                     client.println("Connection: close");
    //                     client.println();

    //                     doc["ledState"] = ledState;
    //                     doc["ledPin"] = ledPin;

    //                     serializeJson(doc, jsonResponse);
    //                     client.println(jsonResponse);

    //                     // The HTTP response ends with another blank line
    //                     client.println();

    //                     // Break out of the while loop
    //                     break;
    //                 }
    //                 else
    //                 {
    //                     currentLine = "";
    //                 }
    //             }
    //             else if (c != '\r')
    //             {
    //                 currentLine += c;
    //             }

    //             command = header.substring(5, 7);
    //             speed = header.substring(8, 12);
    //             speedSign = speed.substring(0, 1);
    //             if (speedSign == "-")
    //             {
    //                 speed = speed.substring(1, 4);
    //             }
    //             else
    //             {
    //                 speed = speed.substring(0, 3);
    //             }

    //             speedInt = speed.toInt();

    //             Serial.println(command);
    //             Serial.println(speed);

    //             if (command == "on")
    //             {
    //                 digitalWrite(ledPin, HIGH);
    //                 ledState = "ON";

    //                 ledcWrite(0, 255);
    //                 digitalWrite(M1_IN1, HIGH);
    //                 digitalWrite(M1_IN2, LOW);

    //                 if (speedInt > 0 && speedInt < 180)
    //                 {
    //                     // Serial.println("Speed is: " + String(speedInt));
    //                     // myServo.write(speedInt);
    //                 }
    //             }

    //             if (command == "of")
    //             {
    //                 digitalWrite(M1_IN1, LOW);
    //                 digitalWrite(M1_IN2, LOW);

    //                 digitalWrite(ledPin, LOW);
    //                 ledState = "OFF";
    //             }
    //         }
    //     }
    //     // Clear the header variable
    //     header = "";

    //     // Close the connection
    //     client.stop();
    //     // Serial.println("Client disconnected.");
    //     // Serial.println("");
    // }
}
