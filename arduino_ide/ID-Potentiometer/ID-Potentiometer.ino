//#include "Servo.h"

//Servo servo;
int potent;

void setup() {
  Serial.begin(9600);

  //servo.attach(A5);
}

void loop() {
  potent = analogRead(A5);
  Serial.println("Value is: "+ String(potent));
  delay(200);
}
