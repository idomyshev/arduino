#include <Arduino.h>
#include <WiFi.h>
#include <ESP32Servo.h>

Servo myServo;
int servoPin = 18;

// WiFi credentials - Connect to iPhone Personal Hotspot or any WiFi
// Change these to match your iPhone hotspot name and password
const char *ssid = "DIGIFIBRA-6GDf"; // Your iPhone hotspot name
const char *password = "";           // Your iPhone hotspot password

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
    // Disable watchdog timers to prevent crashes during WiFi operations
    disableCore0WDT();
    disableCore1WDT();

    // TEMPORARILY DISABLED: Servo might cause power issues
    // Uncomment these lines after WiFi connection is stable
    // myServo.attach(servoPin);
    // myServo.write(0);

    // Initialize the LED pin as an output
    pinMode(ledPin, OUTPUT);
    digitalWrite(ledPin, LOW); // LED is off initially

    // Start serial communication
    Serial.begin(115200);
    delay(2000); // Increased delay for stability

    // Connect to WiFi (iPhone hotspot or home WiFi)
    Serial.println("\n========================================");
    Serial.println("Connecting to WiFi...");
    Serial.print("SSID: ");
    Serial.println(ssid);

    // Configure WiFi settings
    WiFi.mode(WIFI_STA); // Set WiFi to station mode
    WiFi.setAutoReconnect(true);
    WiFi.persistent(false); // Don't save WiFi config to flash (faster, less wear)
    delay(100);

    WiFi.begin(ssid, password);

    // Wait for connection with timeout
    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 40)
    {
        delay(500);
        Serial.print(".");
        attempts++;
        yield(); // Feed the watchdog
    }

    if (WiFi.status() == WL_CONNECTED)
    {
        delay(1000); // Wait for connection to stabilize

        Serial.println("\n✓ Connected to WiFi!");
        Serial.println("========================================");
        Serial.println("Network Information:");
        Serial.print("  IP Address: ");
        Serial.println(WiFi.localIP());
        Serial.print("  Gateway:    ");
        Serial.println(WiFi.gatewayIP());
        Serial.print("  Signal:     ");
        Serial.print(WiFi.RSSI());
        Serial.println(" dBm");
        Serial.println("========================================");
        Serial.print("\n🌐 Open in browser: http://");
        Serial.println(WiFi.localIP());
        Serial.println();

        // Start the web server
        delay(500);
        server.begin();
        Serial.println("✓ Web server started!");
        Serial.println("========================================\n");
    }
    else
    {
        Serial.println("\n✗ Failed to connect to WiFi");
        Serial.println("Please check:");
        Serial.println("  1. WiFi network is available");
        Serial.println("  2. SSID and password are correct");
        Serial.println("  3. ESP32 is in range");
        Serial.println("\nRestarting ESP32 in 5 seconds...");
        delay(5000);
        ESP.restart();
    }
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

                    // SERVO TEMPORARILY DISABLED - uncomment after WiFi is stable
                    // if (speedInt > 0 && speedInt < 180)
                    // {
                    //     Serial.println("Speed is: " + String(speedInt));
                    //     myServo.write(speedInt);
                    // }
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
