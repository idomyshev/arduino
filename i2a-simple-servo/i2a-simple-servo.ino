#include "Servo.h"

Servo rudder;

void setup() {
  rudder.attach(6);

}

void loop() {
  rudder.writeMicroseconds(550);
  delay(5000);
  rudder.writeMicroseconds(1450);
  delay(5000);
  rudder.writeMicroseconds(2350);
  delay(5000);
}
