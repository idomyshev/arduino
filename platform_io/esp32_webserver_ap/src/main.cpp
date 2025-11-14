#include <Arduino.h>
#include <WiFi.h>
#include <ESP32Servo.h>

Servo myServo;
int servoPin = 18;

// Set the ESP32 as an access point
const char *ssid = "ESP32-AP";
const char *password = "Angara86**"; // Password is optional

// Set web server port number to 80
WiFiServer server(80);

// Variable to store the HTTP request
String header;

// On-board LED is connected to GPIO 2
const int ledPin = 2;

// Current state of the LED
String ledState = "OFF";

String command = "";
String speed = "";
String speedSign = "";

int speedInt = 0;

void setup()
{
    myServo.attach(servoPin);
    myServo.write(0);

    // Initialize the LED pin as an output
    pinMode(ledPin, OUTPUT);
    digitalWrite(ledPin, LOW); // LED is off initially

    // Start serial communication
    Serial.begin(115200);

    // Set up ESP32 as an access point
    Serial.println("Setting up access point...");
    WiFi.softAP(ssid, password);

    // Print the IP address
    Serial.println("Access point created.");
    Serial.print("IP Address: ");
    Serial.println(WiFi.softAPIP());

    // Start the server
    server.begin();
}

void loop()
{
    WiFiClient client = server.available(); // Listen for incoming clients

    if (client)
    { // If a new client connects
        // Serial.println("New Client.");          // Print a message in the serial monitor
        String currentLine = ""; // Make a String to hold incoming data from the client
        while (client.connected())
        { // Loop while the client is connected
            if (client.available())
            {                           // If there's bytes to read from the client,
                char c = client.read(); // Read a byte
                // Serial.write(c);                    // Print it out to the serial monitor
                header += c;
                if (c == '\n')
                { // If the byte is a newline character
                    if (currentLine.length() == 0)
                    {
                        // HTTP response
                        client.println("HTTP/1.1 200 OK");
                        client.println("Content-type:text/html");
                        client.println("Connection: close");
                        client.println();

                        // Display the web page
                        client.println("<!DOCTYPE html><html>");
                        client.println("<head><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">");
                        client.println("<title>Ilia's ESP32</title></head>");

                        // Display current LED state
                        client.println("<p>LED status is " + ledState + "</p>");

                        // The HTTP response ends with another blank line
                        client.println();

                        // Break out of the while loop
                        break;
                    }
                    else
                    {
                        currentLine = "";
                    }
                }
                else if (c != '\r')
                {
                    currentLine += c;
                }

                command = header.substring(5, 7);
                speed = header.substring(8, 12);
                speedSign = speed.substring(0, 1);
                if (speedSign == "-")
                {
                    speed = speed.substring(1, 4);
                }
                else
                {
                    speed = speed.substring(0, 3);
                }

                speedInt = speed.toInt();

                Serial.println(command);
                Serial.println(speed);

                if (command == "on")
                {
                    digitalWrite(ledPin, HIGH);
                    ledState = "ON";

                    if (speedInt > 0 && speedInt < 180)
                    {
                        Serial.println("Speed is: " + String(speedInt));
                        myServo.write(speedInt);
                    }
                }

                if (command == "of")
                {
                    digitalWrite(ledPin, LOW);
                    ledState = "OFF";
                }
            }
        }
        // Clear the header variable
        header = "";

        // Close the connection
        client.stop();
        // Serial.println("Client disconnected.");
        // Serial.println("");
    }
}
