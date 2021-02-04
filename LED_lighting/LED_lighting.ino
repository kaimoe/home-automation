#include <SPI.h>
#include <WiFiNINA.h>
#include <WiFiUdp.h>
#include <RTCZero.h>
#include <Regexp.h>

#include "arduino_secrets.h"

RTCZero rtc;

//RGB pins
const int RED_PIN = 3;
const int GREEN_PIN = 4;
const int BLUE_PIN = 5;
#include "led_handling.h"

const String DEFAULT_COLOR = "white";

const bool AUTODIM = true;
const int DIM_START_HOUR = 0;
const int DIM_END_HOUR = 12;
///////please enter your sensitive data in the Secret tab/arduino_secrets.h
char ssid[] = SECRET_SSID;        // your network SSID (name)
char pass[] = SECRET_PASS;    // your network password (use for WPA, or use as key for WEP)
int keyIndex = 0;                           // your network key Index number (needed only for WEP)

int status = WL_IDLE_STATUS;

const int GMT = 2; //change this to adapt it to your time zone

WiFiServer server(80);

void setup() {
  Serial.begin(115200);

	pinMode(RED_PIN, OUTPUT);
	pinMode(GREEN_PIN, OUTPUT);
	pinMode(BLUE_PIN, OUTPUT);
	handlePayload(DEFAULT_COLOR);

  if (WiFi.status() == WL_NO_SHIELD) {
    Serial.println("WiFi shield not present");
    while (true);
  }

  // attempt to connect to WiFi network:
  while ( status != WL_CONNECTED) {
    Serial.print("Attempting to connect to SSID: ");
    Serial.println(ssid);
    // Connect to WPA/WPA2 network. Change this line if using open or WEP network:
    status = WiFi.begin(ssid, pass);
    // wait 10 seconds for connection:
    delay(10000);
  }

  printWiFiStatus();

  rtc.begin();

  unsigned long epoch;
  int numberOfTries = 0, maxTries = 10;

  do {
    epoch = WiFi.getTime();
    numberOfTries++;
  } while ((epoch == 0) && (numberOfTries < maxTries));

  if (numberOfTries == maxTries) {
    Serial.print("NTP unreachable!!");
    while (1);
  } else {
    Serial.print("Epoch received: ");
    Serial.println(epoch);
    rtc.setEpoch(epoch);
    Serial.println();
  }

  server.begin();
}

void loop() {
	WiFiClient client = server.available();

  if (client) {

    Serial.println("new client");
    String currentLine = "";

    while (client.connected()) {

      if (client.available()) {

        char c = client.read();

        Serial.write(c);

        if (c == '\n' || c == '\r') {
					currentLine = "";

        } else if (c != '\r') {  // if you got anything else but a carriage return character,
          currentLine += c;      // add it to the end of the currentLine

        }

				if (client.peek() == -1) {
					client.println("HTTP/1.1 200 OK");
					client.println("Content-type:text/plain");
					client.println();

					// the content of the HTTP response follows the header:
					client.print("");

					// The HTTP response ends with another blank line:
					client.println();


					char temp[100];
					strcpy(temp, currentLine.c_str());
					MatchState ms;
					ms.Target(temp);
					char result = ms.Match("{\"payload\"[:%s]+\"([%a%s]+)\"}", 0);

					if (result == REGEXP_NOMATCH) {
						Serial.println("No match");
						break;
					}

					char payload[20];
					ms.GetCapture(payload, 0);

					handlePayload(payload);

					break;
				}
      }
    }

    // close the connection:
    client.stop();
    Serial.println("client disonnected\n");
  }
	delay(10);
}

void printTime()
{

  print2digits(rtc.getHours() + GMT);

  Serial.print(":");

  print2digits(rtc.getMinutes());

  Serial.print(":");

  print2digits(rtc.getSeconds());

  Serial.println();
}

void printDate()
{

  Serial.print(rtc.getDay());

  Serial.print("/");

  Serial.print(rtc.getMonth());

  Serial.print("/");

  Serial.print(rtc.getYear());

  Serial.print(" ");
}

void printWiFiStatus() {

  // print the SSID of the network you're attached to:

  Serial.print("SSID: ");

  Serial.println(WiFi.SSID());

  // print your WiFi shield's IP address:

  IPAddress ip = WiFi.localIP();

  Serial.print("IP Address: ");

  Serial.println(ip);

  // print the received signal strength:

  long rssi = WiFi.RSSI();

  Serial.print("signal strength (RSSI):");

  Serial.print(rssi);

  Serial.println(" dBm");
}

void print2digits(int number) {

  if (number < 10) {

    Serial.print("0");

  }

  Serial.print(number);
}
