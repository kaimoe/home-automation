#include <SPI.h>
#include <WiFiNINA.h>
#include <WiFiUdp.h>
#include <RTCZero.h>
#include <Regexp.h>

#include "arduino_secrets.h"

RTCZero rtc;
const int GMT = 2; //set to local timezone offset

//RGB pins
#define RED_PIN 4
#define GREEN_PIN 5
#define BLUE_PIN 3
//time in ms between loops
#define LOOP_DELAY 10

const char DEFAULT_COLOR[] = "purple";

//autodim settings
const bool AUTODIM = true;
const int DIM_START_HOUR = 0;
const int DIM_END_HOUR = 12;
int last_dimmed_day = 0;
int last_undimmed_day = 0;
//number of loop cycles to check for dimming changes
const int dim_counter_max = 1000;
int dim_counter = dim_counter_max;

#include "led_handling.h"

//enter in the Secret tab/arduino_secrets.h
char ssid[] = SECRET_SSID;
char pass[] = SECRET_PASS;

int status = WL_IDLE_STATUS;

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
	int numberOfTries = 0, maxTries = 20;

	do {
		epoch = WiFi.getTime();
		numberOfTries++;
	} while ((epoch == 0) && (numberOfTries < maxTries));

	if (numberOfTries == maxTries) {
		Serial.print("NTP unreachable!!");
		while (1) {
			handlePayload("red");
			delay(5000);
			handlePayload("black");
			delay(5000);
		}
	} else {
		Serial.print("Epoch received: ");
		Serial.println(epoch);
		rtc.setEpoch(epoch);
		Serial.println();
	}

	server.begin();
}

void loop() {
	if (AUTODIM) autoDimming();

	WiFiClient client = server.available();

	if (client) {
		Serial.println("New client");
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

				if (client.peek() == -1) {//end of request
					client.println("HTTP/1.1 200 OK");
					client.println("Content-type:text/plain");
					client.println();

					// the content of the HTTP response follows the header:
					client.print("");

					// The HTTP response ends with another blank line:
					client.println();

					//pattern match the payload
					char temp[100];
					strcpy(temp, currentLine.c_str());
					MatchState ms;
					ms.Target(temp);
					char result = ms.Match("{\"payload\"[:%s]+\"([%a%s]+)\"}", 0);

					if (result == REGEXP_NOMATCH) {
						Serial.println("No match");
						break;
					}

					char payload[30];
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
	delay(LOOP_DELAY);
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
