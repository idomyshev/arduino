#include "Servo.h"

Servo motor;
int minMotorVal = 800; // Could not be less than 800;
int maxMotorVal = 860; // Could be not more than 2300;

void setup() {
  Serial.begin(9600);
  motor.attach(2);
  motor.writeMicroseconds(2300);
  delay(1000);
  motor.writeMicroseconds(800);
  delay(6000);
}

void loop() {
  int analogVal = analogRead(0);
  int motorVal = constrain(map(analogVal, 0, 1023, minMotorVal, maxMotorVal), minMotorVal, maxMotorVal);
  motor.writeMicroseconds(motorVal);
  Serial.println(motorVal);
}
