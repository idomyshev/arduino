#include <SPI.h>
#include "nRF24L01.h"
#include "RF24.h"
#include "Servo.h"

RF24 radio(9, 10);  // "создать" радио-модуль на пинах 9 и 10 Для Уно
byte address[][6] = {"1Node", "2Node", "3Node", "4Node", "5Node", "6Node"}; //возможные номера труб

Servo servo;
Servo motor;

int servoVal;
int motorVal;

int minMotorFactoryVal = 800;
int maxMotorFactoryVal = 2300;

byte pipeNo;  
int gotByte; 
String inputString;

void setup() {
  Serial.begin(9600);         // открываем порт для связи с ПК
  radio.begin();              // активировать модуль
  radio.setAutoAck(1);        // режим подтверждения приёма, 1 вкл 0 выкл
  radio.setRetries(0, 15);    // (время между попыткой достучаться, число попыток)
  radio.enableAckPayload();   // TODO: Do I need it? разрешить отсылку данных в ответ на входящий сигнал
  radio.setPayloadSize(32);   // размер пакета, в байтах

  radio.openReadingPipe(1, address[0]);   // хотим слушать трубу 0
  radio.setChannel(0x60);     // выбираем канал (в котором нет шумов!)

  radio.setPALevel (RF24_PA_MAX);   // уровень мощности передатчика. На выбор RF24_PA_MIN, RF24_PA_LOW, RF24_PA_HIGH, RF24_PA_MAX
  radio.setDataRate (RF24_250KBPS); // скорость обмена. На выбор RF24_2MBPS, RF24_1MBPS, RF24_250KBPS
  //должна быть одинакова на приёмнике и передатчике!
  //при самой низкой скорости имеем самую высокую чувствительность и дальность!!

  radio.powerUp();        // начать работу
  radio.startListening(); // начинаем слушать эфир, мы приёмный модуль

  motor.attach(5);
  servo.attach(6);

  // Calibrate the brushless motor;
  motor.writeMicroseconds(maxMotorFactoryVal); // Set maximum speed;
  delay(1000);
  motor.writeMicroseconds(minMotorFactoryVal); // Set minimum speed;
  delay(6000);
}

void loop() {
  //Serial.println("Hi! Start reading radio...");

  while (radio.available(&pipeNo)) {
    // Radio;
    radio.read(&gotByte, sizeof(gotByte));
    inputString = String(gotByte);
    //Serial.println("Radio is: " + inputString);

    // Servo;
    servoVal = map(gotByte, 0, 64, 125, 55);
    //servoVal = constrain(servoVal, 800, 2300);
    Serial.println("Rudder value is: " + String(servoVal));
    servo.write(servoVal);

    // // Motor;
    // motorVal = map(gotByte, 0, 64, 0, 255);
    // Serial.println("Motor is: " + String(motorVal));
    // analogWrite(EN12, motorVal);
    // digitalWrite(A1, HIGH);
    // digitalWrite(A2, LOW);


    delay(50);
  }
}
