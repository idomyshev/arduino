#include <ESP32Servo.h>

Servo myServo;
int servoPin = 18;

void setup() {
  myServo.attach(servoPin);
  // Serial.begin(115200);

}

void loop() {
  myServo.write(0);
  delay(1000);
  myServo.write(90);
  delay(1000);
  myServo.write(180);
  delay(1000);
  
  // if (Serial.available()) {
  //   int angle = Serial.parseInt();
  //   myServo.write(angle);
  // }

}
