#include <Arduino.h>
#include <WiFi.h>
#include <ESP32Servo.h>
#include <ArduinoJson.h>
#include <ESPAsyncWebServer.h>
#include <AsyncJson.h>

Servo myServo;
int servoPin = 18;

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

void processCommand(String jsonCommand);
void updateMotors();
void stopAllMotors();

// Set the ESP32 as an access point
const char *ssid = "ESP32-AP";
const char *password = "Angara86**"; // Password is optional

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

    // myServo.attach(servoPin);
    // myServo.write(0);

    // Initialize the LED pin as an output
    pinMode(ledPin, OUTPUT);
    digitalWrite(ledPin, LOW); // LED is off initially

    // Start serial communication
    Serial.begin(115200);

    // Set up ESP32 as an access point
    Serial.println("Setting up access point...");
    WiFi.softAP(ssid, password);

    // Print the IP address
    Serial.println("Access point created.");
    Serial.print("IP Address: ");
    Serial.println(WiFi.softAPIP());

        // Обработка POST запросов с JSON телом
        AsyncCallbackJsonWebHandler *handler = new AsyncCallbackJsonWebHandler("/", [](AsyncWebServerRequest *request, JsonVariant &json) {
            JsonObject jsonObj = json.as<JsonObject>();
            
            // Обработка JSON данных
            if (jsonObj["command"].is<String>())
            {
                String cmd = jsonObj["command"];
                Serial.println("Command: " + cmd);
                
                if (cmd == "on")
                {
                    digitalWrite(ledPin, HIGH);
                    ledState = "ON";
                    
                    // Обработка моторов из JSON
                    if (jsonObj["motor"].is<int>() && jsonObj["speed"].is<int>()) {
                        int motor = jsonObj["motor"];
                        int speed = jsonObj["speed"];
                        Serial.println("Motor: " + String(motor) + ", Speed: " + String(speed));
                        // Ваша логика управления моторами
                        ledcWrite(0, 255);
                        digitalWrite(M1_IN1, HIGH);
                        digitalWrite(M1_IN2, LOW);
                    }
                }
                else if (cmd == "off")
                {
                    digitalWrite(ledPin, LOW);
                    ledState = "OFF";
                    digitalWrite(M1_IN1, LOW);
                    digitalWrite(M1_IN2, LOW);
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
