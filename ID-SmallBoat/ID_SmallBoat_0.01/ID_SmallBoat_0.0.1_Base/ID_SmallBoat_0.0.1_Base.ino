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
  byte pipeNo;  
  int gotByte; int i; int speed;
  String inputString;
  String right; String left; String up; String down;
  bool stopped = true;

  speed = 255;

  Serial.println("Hi! Start reading radio...");

  while (radio.available(&pipeNo)) {        // слушаем эфир со всех труб
    radio.read(&gotByte, sizeof(gotByte));  // чиатем входящий сигнал

    i++;

    Serial.println(i);

    analogWrite(EN12, 255);
    analogWrite(EN34, 255);

    //Serial.print("Recieved: ");
    //Serial.println(gotByte);
    inputString = String(gotByte);
    right = inputString.substring(1, 2);
    left = inputString.substring(2, 3);
    down = inputString.substring(3, 4);
    up = inputString.substring(4, 5);

    

    if(right == "1") {
      Serial.println("right");
      //servo.write(0);

      digitalWrite(A1, HIGH);
      digitalWrite(A2, LOW);
      digitalWrite(A3, HIGH);
      digitalWrite(A4, LOW);

    }

    if(left == "1") {
      Serial.println("left");

        digitalWrite(A1, LOW);
        digitalWrite(A2, HIGH);
        digitalWrite(A3, LOW);
        digitalWrite(A4, HIGH);

        stopped = false;
    }

    if(up == "1") {
      Serial.println("up");

        digitalWrite(A1, HIGH);
        digitalWrite(A2, LOW);
        digitalWrite(A3, LOW);
        digitalWrite(A4, HIGH);

        stopped = false;
      
      //analogWrite(EN12, 255);
      // if (speed <= 247) {
      //   speed+=8;
      //   //analogWrite(EN12, speed);
        
      // }
    }

    if(down == "1") {
      Serial.println("down");  
      
      if (stopped == true) {
        digitalWrite(A1, LOW);
        digitalWrite(A2, HIGH);
        digitalWrite(A3, HIGH);
        digitalWrite(A4, LOW);

        stopped = false;
      } else {
        digitalWrite(A1, LOW);
        digitalWrite(A2, LOW);
        digitalWrite(A3, LOW);
        digitalWrite(A4, LOW);

        stopped = true;
      }      

      // if (speed >= 8) {
      //  speed-=8;
      //  //analogWrite(EN12, speed);
      // }
      
    }

    delay(50);

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
}
