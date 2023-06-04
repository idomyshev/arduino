/*   Данный скетч делает следующее: передатчик (TX) отправляет массив
     данных, который генерируется согласно показаниям с кнопки и с
     двух потенциомтеров. Приёмник (RX) получает массив, и записывает
     данные на реле, сервомашинку и генерирует ШИМ сигнал на транзистор.
    by AlexGyver 2016
*/

#include <SPI.h>          // библиотека для работы с шиной SPI
#include "nRF24L01.h"     // библиотека радиомодуля
#include "RF24.h"         // ещё библиотека радиомодуля

byte address[][6] = {"1Node", "2Node", "3Node", "4Node", "5Node", "6Node"}; //возможные номера труб

bool radioOn = true; // Developer, switch it off if your wi-fi module is next to you and you are not testing wi-fi now;
int loopDelay = 50;
int intPayload;
String strPayload;

int minSpeed = 10;
int maxSpeed = 40;
int initialValueSpeed = minSpeed;
int speed = initialValueSpeed; // Current speed;
int stepSpeed = 1;

int minRudder = 0;
int maxRudder = 90;
int initialValueRudder = minRudder + (maxRudder - minRudder) / 2;
int rudder = initialValueRudder; // Current rudder value;
int stepRudder = 1;

int buttonUpPin = 8;
int buttonDownPin = 7;
int buttonRightPin = 6;
int buttonLeftPin = 5;

//if (radioOn) {
 // "создать" модуль на пинах 9 и 10 Для Уно
RF24 radio(9, 10);
//RF24 radio(9,53); // для Меги
//}

void setup() {
  Serial.begin(9600);         // открываем порт для связи с ПК

  if (radioOn) { 
    radio.begin();              // активировать модуль
    radio.setAutoAck(1);        // режим подтверждения приёма, 1 вкл 0 выкл
    radio.setRetries(0, 15);    // (время между попыткой достучаться, число попыток)
    radio.enableAckPayload();   // разрешить отсылку данных в ответ на входящий сигнал
    radio.setPayloadSize(32);   // размер пакета, в байтах

    radio.openWritingPipe(address[0]);  // мы - труба 0, открываем канал для передачи данных
    radio.setChannel(0x60);             // выбираем канал (в котором нет шумов!)

    radio.setPALevel (RF24_PA_MAX);   // уровень мощности передатчика. На выбор RF24_PA_MIN, RF24_PA_LOW, RF24_PA_HIGH, RF24_PA_MAX
    radio.setDataRate (RF24_250KBPS); // скорость обмена. На выбор RF24_2MBPS, RF24_1MBPS, RF24_250KBPS
    //должна быть одинакова на приёмнике и передатчике!
    //при самой низкой скорости имеем самую высокую чувствительность и дальность!!

    radio.powerUp();        // начать работу
    radio.stopListening();  // не слушаем радиоэфир, мы передатчик
  }

  Serial.println(radioOn ? "Radio is ON" : "Radio is OFF");

  pinMode(buttonUpPin, INPUT_PULLUP);
  pinMode(buttonDownPin, INPUT_PULLUP);
  pinMode(buttonRightPin, INPUT_PULLUP);
  pinMode(buttonLeftPin, INPUT_PULLUP);
}

void loop() {
  int btnUp = !digitalRead(buttonUpPin);
  int btnDown = !digitalRead(buttonDownPin);
  int btnRight = !digitalRead(buttonRightPin);
  int btnLeft = !digitalRead(buttonLeftPin);

  if (btnUp) {
    rudder = initialValueRudder;
  }

  if (btnUp && speed < maxSpeed) {
    speed += stepSpeed;
  }
  

  if (btnDown && speed > minSpeed) {
    speed -= stepSpeed;
  }

    if (btnRight && rudder < maxRudder) {
    rudder += stepRudder;
  }
  

  if (btnLeft && rudder > minRudder) {
    rudder -= stepRudder;
  }

  // Serial.println("Speed is: " + String(speed));
  // Serial.println("Rudder is: " + String(rudder));
  
  strPayload = String(speed) + String(rudder);
  // Serial.println("Payload is: " + strPayload);
  // Serial.println("");

  if (radioOn && strPayload) {
    intPayload = strPayload.toInt();
    radio.write(&intPayload, sizeof(intPayload));
  }

  //delay(10);
}
