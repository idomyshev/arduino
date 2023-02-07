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
  // int analogVal = analogRead(0);
  // int motorVal = constrain(map(analogVal, 0, 1023, minMotorVal, maxMotorVal), minMotorVal, maxMotorVal);
  // motor.writeMicroseconds(motorVal);
  
  motor.writeMicroseconds(800);
  Serial.println("phase0");
  delay(2000);

  motor.writeMicroseconds(860);
  Serial.println("phase1");
  delay(2000);
  
  motor.writeMicroseconds(880);
  Serial.println("phase2");
  delay(2000);
  
  motor.writeMicroseconds(900);
  Serial.println("phase3");
  delay(2000);

  motor.writeMicroseconds(920);
  Serial.println("phase4");
  delay(2000);

  //Serial.println(motorVal);
}
