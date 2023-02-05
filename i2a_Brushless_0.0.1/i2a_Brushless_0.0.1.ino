#include "Servo.h"

Servo motor;

void setup() {
  Serial.begin(9600);
  motor.attach(2);
}

void loop() {
  int analogVal = analogRead(0);
  int motorVal = constrain(map(analogVal, 0, 1023, 800, 2300), 800, 2300);
  motor.writeMicroseconds(motorVal);
  Serial.println(motorVal);
}
