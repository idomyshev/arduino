/*   Данный скетч делает следующее: передатчик (TX) отправляет массив
     данных, который генерируется согласно показаниям с кнопки и с
     двух потенциомтеров. Приёмник (RX) получает массив, и записывает
     данные на реле, сервомашинку и генерирует ШИМ сигнал на транзистор.
    by AlexGyver 2016
*/

#include <SPI.h>
#include "nRF24L01.h"
#include "RF24.h"
#include "Servo.h"

RF24 radio(9, 10);  // "создать" модуль на пинах 9 и 10 Для Уно
//RF24 radio(9,53); // для Меги

byte address[][6] = {"1Node", "2Node", "3Node", "4Node", "5Node", "6Node"}; //возможные номера труб

#define A1 4
#define A2 2
#define EN12 5

#define A3 6
#define A4 7
#define EN34 3

Servo servo;
int loopDelay;
int loopStep = 0;
byte pipeNo;  
int intPayload;
String strPayload;

int speed; // Speed value;
int minSpeed = 10; // Value should be the same with RC;
int maxSpeed = 40; // Value should be the same with RC;
int motorSpeed;
int minMotorSpeed = 110;
int maxMotorSpeed = 255;

int rudder; // Rudder value;
int minRudder = 10; // Value should be the same with RC;
int maxRudder = 40; // Value should be the same with RC;

void setup() {
  Serial.begin(9600);         // открываем порт для связи с ПК
  radio.begin();              // активировать модуль
  radio.setAutoAck(1);        // режим подтверждения приёма, 1 вкл 0 выкл
  radio.setRetries(0, 15);    // (время между попыткой достучаться, число попыток)
  radio.enableAckPayload();   // разрешить отсылку данных в ответ на входящий сигнал
  radio.setPayloadSize(32);   // размер пакета, в байтах

  radio.openReadingPipe(1, address[0]);   // хотим слушать трубу 0
  radio.setChannel(0x60);     // выбираем канал (в котором нет шумов!)

  radio.setPALevel (RF24_PA_MAX);   // уровень мощности передатчика. На выбор RF24_PA_MIN, RF24_PA_LOW, RF24_PA_HIGH, RF24_PA_MAX
  radio.setDataRate (RF24_250KBPS); // скорость обмена. На выбор RF24_2MBPS, RF24_1MBPS, RF24_250KBPS
  //должна быть одинакова на приёмнике и передатчике!
  //при самой низкой скорости имеем самую высокую чувствительность и дальность!!

  radio.powerUp();        // начать работу
  radio.startListening(); // начинаем слушать эфир, мы приёмный модуль

  //servo.attach(3);

  pinMode(A1, OUTPUT);
  pinMode(A2, OUTPUT);
  pinMode(EN12, OUTPUT);
  pinMode(A3, OUTPUT);
  pinMode(A4, OUTPUT);
  pinMode(EN34, OUTPUT);
}

void loop() {
  while (radio.available(&pipeNo)) {        // слушаем эфир со всех труб
    radio.read(&intPayload, sizeof(intPayload));  // чиатем входящий сигнал
    strPayload = String(intPayload);

    speed = strPayload.substring(0, 2).toInt();

    if (speed > minSpeed) {
      //motorSpeed = speed - minSpeed + minMotorSpeed;
      motorSpeed = map(speed, minSpeed, maxSpeed, minMotorSpeed, maxMotorSpeed);
      motorSpeed = constrain(motorSpeed, minMotorSpeed, maxMotorSpeed);
    } else {
      motorSpeed = 0;
    }

    rudder = strPayload.substring(2, 4).toInt();

    analogWrite(EN12, motorSpeed);
    analogWrite(EN34, motorSpeed);

    digitalWrite(A1, HIGH);
    digitalWrite(A2, LOW);
    digitalWrite(A3, LOW);
    digitalWrite(A4, HIGH); 

    // TODO: Uncomment when start using servo;
    // servo.write(0);
    // delay(1000);
    // servo.write(45);
    // delay(1000);
    // servo.write(90);
    // delay(1000);
    // servo.write(135);
    // delay(1000);
    // servo.write(180);
    // delay(1000);
  }

  
  if (!loopStep) {
    Serial.println("Motor speed is: "+ String(motorSpeed));
    Serial.println("Rudder value is: "+ String(rudder));
    Serial.println("loopStep: " + String(loopStep)); 
    Serial.println("");
  }

  
  loopStep = loopStep == 999999 ? 0: loopStep + 1;

  delay(loopDelay);
}
