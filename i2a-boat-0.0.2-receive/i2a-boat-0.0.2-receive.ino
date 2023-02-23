#include <SPI.h>
#include "nRF24L01.h"
#include "RF24.h"
#include "Servo.h"

// Brushless motor;
Servo motor;
Servo rudder;
int minMotorVal = 800; // Could not be less than 800;
int maxMotorVal = 2300; // Could be not more than 2300; Soft power value is 1260;
int minMotorFactoryVal = 800;
int maxMotorFactoryVal = 2300;
int motorSpeed = 0;
int rudderValue = 90;

// Radio;
RF24 radio(9, 10); // Create radio module on pins 9, 10 for Nano/Uno;
byte address[][6] = {"1Node", "2Node", "3Node", "4Node", "5Node", "6Node"}; // possible radio pipes numbers;

// Leds and buttons;
#define redLed 2
#define yellowLed 3
#define greenLed 4
#define blueLed 5
#define cmdBtnLeft 1
#define cmdBtnRight 2
#define cmdBtnDown 3
#define cmdBtnUp 4
#define cmdBtnFunc1 11
#define cmdBtnFunc2 12
#define cmdBtnFunc3 13
#define cmdBtnFunc4 14
#define cmdBtnFunc5 15

void setup() {
  // Switch on serial port;
  Serial.begin(9600);    

  radio.begin();              // activate radio module;
  radio.setAutoAck(1);        // receive mode (1 - switched on);
  radio.setRetries(0, 15);    // (1 - period between tries and, 2 - number of tries);
  radio.enableAckPayload();   // allow to send data as answer for input signal; 
  radio.setPayloadSize(32);   // package size in bytes;

  radio.openReadingPipe(1, address[0]);   // listen to pipe number 0;
  radio.setChannel(0x60);     // choose channel (without noises!);

  radio.setPALevel (RF24_PA_MAX);   // level of transmitter power; options: RF24_PA_MIN, RF24_PA_LOW, RF24_PA_HIGH, RF24_PA_MAX;
  // Exchange speed: should be same on transmitter and receiver;
  // For lowest speed we have highest sensibility and distance;
  radio.setDataRate (RF24_250KBPS); // options: RF24_2MBPS, RF24_1MBPS, RF24_250KBPS
  

  radio.powerUp();        // Switch on radio module;
  radio.startListening(); // Start listen to ether;

  // Pin modes for leds;
  pinMode(redLed, OUTPUT);
  pinMode(yellowLed, OUTPUT);
  pinMode(greenLed, OUTPUT);
  pinMode(blueLed, OUTPUT);

  // Set pin for brushless motor;
  motor.attach(7);
  // Set pin for servo motor;
  rudder.attach(6);
  
  // Calibrate the brushless motor;
  motor.writeMicroseconds(maxMotorFactoryVal); // Set maximum speed;
  delay(1000);
  motor.writeMicroseconds(minMotorFactoryVal); // Set minimum speed;
  delay(6000);
}

void loop() {
  byte pipeNo;  
  int gotByte;  

  while (radio.available(&pipeNo)) {      // Lister to ether from all pipes;
    radio.read(&gotByte, sizeof(gotByte));  // Read input signal;

    // Logic for leds;
    digitalWrite(redLed, gotByte == cmdBtnLeft ? HIGH : LOW);
    digitalWrite(yellowLed, gotByte == cmdBtnUp ? HIGH : LOW);
    digitalWrite(greenLed, gotByte == cmdBtnRight ? HIGH : LOW);
    digitalWrite(blueLed, gotByte == cmdBtnDown ? HIGH : LOW);

    

    // Logic to manage brushless motor speed;
    if (gotByte == cmdBtnUp && motorSpeed < maxMotorVal - minMotorVal) {
      motorSpeed += 5;
    }

    if (gotByte == cmdBtnDown && motorSpeed > 0) {
      motorSpeed -= 5;
    }

    if (gotByte == cmdBtnFunc2) {
      motorSpeed = 0;
    }

    // Logic to manage rudder servo;
    if (gotByte == cmdBtnLeft && rudderValue >= 5) {
      rudderValue -= 5;
    }

    if (gotByte == cmdBtnRight && rudderValue <= 175) {
      rudderValue += 5;
    }

    if (gotByte == cmdBtnFunc1) {
      rudderValue = 90;
    }

    // Give command to brushless motor;
    motor.writeMicroseconds(minMotorVal + motorSpeed);

    // Give command to rudder servo;
    rudder.write(rudderValue);

    Serial.println("command:");
    Serial.println(String(gotByte));
    Serial.println("speed:");
    Serial.println(motorSpeed);
    
    delay(50);
  }
}
