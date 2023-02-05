/*   Данный скетч делает следующее: передатчик (TX) отправляет массив
     данных, который генерируется согласно показаниям с кнопки и с
     двух потенциомтеров. Приёмник (RX) получает массив, и записывает
     данные на реле, сервомашинку и генерирует ШИМ сигнал на транзистор.
    by AlexGyver 2016
*/

#include <SPI.h>          // библиотека для работы с шиной SPI
#include "nRF24L01.h"     // библиотека радиомодуля
#include "RF24.h"         // ещё библиотека радиомодуля

RF24 radio(9, 10); // "создать" модуль на пинах 9 и 10 Для Уно
//RF24 radio(9,53); // для Меги

byte address[][6] = {"1Node", "2Node", "3Node", "4Node", "5Node", "6Node"}; //возможные номера труб

// #define redLed 19
// #define yellowLed 17
// #define greenLed 18

#define remoteYellowLed A3
#define remoteRedLed A2
Servo motor1;

void setup() {
  Serial.begin(9600);         // открываем порт для связи с ПК

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

  // TODO These two pins D1, D2 used for serial data exchange, that's why it's difficult to test same time with using serial port.
  // pinMode(0, INPUT_PULLUP);
  // pinMode(1, INPUT_PULLUP);
  pinMode(2, INPUT_PULLUP); // D2
  pinMode(3, INPUT_PULLUP); // D3
  pinMode(4, INPUT_PULLUP); //D4
  pinMode(5, INPUT_PULLUP); //D5
  pinMode(6, INPUT_PULLUP); //D6
  pinMode(7, INPUT_PULLUP); //D7
  pinMode(8, INPUT_PULLUP); //D8
  pinMode(A0, INPUT_PULLUP); //A0
  pinMode(A1, INPUT_PULLUP); //A0

  // pinMode(redLed, OUTPUT);
  // pinMode(yellowLed, OUTPUT);
  // pinMode(greenLed, OUTPUT);
  
  pinMode(remoteYellowLed, OUTPUT);
  pinMode(remoteRedLed, OUTPUT);


}

void loop() {

  // Define buttons.
  int btnRight = !digitalRead(6);
  int btnDown = !digitalRead(7);
  int btnUp = !digitalRead(8);

  int btnFunc1 = !digitalRead(2);
  int btnFunc2 = !digitalRead(3);
  int btnFunc3 = !digitalRead(4);
  int btnFunc4 = !digitalRead(A0);
  int btnFunc5 = !digitalRead(A1);

  int btnLeft = !digitalRead(5);

  byte command = 0;

  digitalWrite(remoteYellowLed, btnFunc1 ? HIGH : LOW);
  digitalWrite(remoteRedLed, btnFunc2 ? HIGH : LOW);

  if (btnFunc1) command = 11;
  if (btnFunc2) command = 12;
  if (btnFunc3) command = 13;
  if (btnFunc4) command = 14;
  if (btnFunc5) command = 15;
  
  // If more than one button is pushed in up/down/right/left,
  // then only one will be prosessed with priority from highest to lowest: up -> down -> right -> left
  if (btnLeft) command = 1;
  if (btnRight) command = 2;
  if (btnDown) command = 3;
  if (btnUp) command = 4;
  
  Serial.println("send:");
  //String payload = "9" + String(command) + "9";
  //byte payloadNumber = payload.toInt();
  Serial.println(command);
  radio.write(&command, sizeof(command));
  
  //delay(40);
}
