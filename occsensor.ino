/*
 *  HacDC Occupancy Sensor - Arduino Code
 *  Copyright (C) 2010 Arc Riley <arcriley@gmail.com>, haxwithaxe <me@haxwithaxe.net>
 *
 *  This program is free software; you can redistribute it and/or modify
 *  it under the terms of the GNU Affero General Public License as published
 *  by the Free Software Foundation, either version 3 of the License, or
 *  (at your option) any later version.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU Affero General Public License for more details.
 *
 *  You should have received a copy of the GNU Affero General Public License
 *  along with this program; if not, see http://www.gnu.org/licenses
 *
 * Depends on the following external libraries
 * EthernetMulti (for multicast): http://tkkrlab.nl/wiki/Arduino_UDP_multicast
 */

#include <stdio.h>
#include <SPI.h>
#include <Ethernet.h>
#include <EthernetUdp.h>

//#define USE_PIR
#define DEBUG
#define YES true
#define NO false
#define ON true
#define OFF false
#define LOOP_DELAY 100
#define BLINK_LEN 300
#define PAUSE_MS 800
#define CALIBRATION_S 5
#define CALIBRATION_MS 980

// sensor_states positions
#define HALL_LIGHT 0
#define HALL_PIR 1
#define MAIN_LIGHT 2
#define MAIN_PIR 3
#define WORK_LIGHT 4
#define WORK_PIR 5

//Ethernet defines
#define MAC	{ 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 }
#define UDP_PORT 5606
#define UDP_LPORT 9001
#define MSGBUFSIZE	256
#define PACKETSIZE        320
#define HEADER  "POST /occsensor/status HTTP/1.0\n\nContent-Type: text/json\n"
#define HTTP_POWERED_ON	"{\"status\":true, \"special\":true,\"message\":\"powered on\"}"
#define UDP_TX_PACKET_MAX_SIZE 24

// constants 
const int biLed = 13;
const int hallLight = 0; //pin
const int hallThreshold = 128; // threshold for on/off
const int hallPIR = 13; //pin CHECK ME
const int mainLight = 1; //pin
const int mainThreshold = 32; // threshold for on/off
const int workLight = 2; //pin
const int workThreshold = 128; // threshold for on/off
const int mainPIR = 11; //pin
const int workPIR = 12; //pin
const int ttl = 5000; // minimum frequency for data updates in ms
const int calibrationTime = 30; // PIR calibration time in seconds
const int waitForHigh = 10; // cycles to wait before considering the high value motion

//Ethernet setup
byte mac[] = MAC;
IPAddress ipAddr(192, 168, 26, 6);
IPAddress targetIpAddr(224, 0, 0, 42);
uint8_t port = UDP_PORT; //TX
uint8_t localPort = UDP_LPORT; //RX unused
// An EthernetUDP instance to let us send and receive packets over UDP
EthernetUDP Udp;

// variables
boolean value = OFF; // variable for each sensor's value
boolean update = NO; // do i need to update?
int timeout = 0; // last time the data was updated
unsigned long lastHigh = 0;
unsigned long firstHigh = 0;

// info storage
char msg[MSGBUFSIZE]; // json string
uint8_t *sensor_states;  //sensor states
unsigned long last_update = 0; // milliseconds of last update

// initialize sensor states
int hallPIRStatus = LOW;
int mainPIRStatus = LOW;
int workPIRStatus = LOW;

// shortcuts
inline void digitalPullup(byte pin, boolean b) {  
  pinMode(pin, INPUT);  
  digitalWrite(pin, b?HIGH:LOW); 
}

void blink(void) {
  digitalWrite(biLed, HIGH);   // turn the LED on (HIGH is the voltage level)
  delay(BLINK_LEN);               // wait for a second
  digitalWrite(biLed, LOW);      // turn the LED off by making the voltage LOW
}
void blinkf(int blinks, int pauses) {
  int b = 0;
  for (b=0; b < blinks; b++) {
    blink();
    int p = 0;
    for (p=0; p < pauses; p++) {
      delay(PAUSE_MS);
    }
  }
}

void blinkn(int times) {
  int i = 0;
  for (i=0; i < times; i++) {
    blink();
  }
}
#if defined(__AVR_ATmega1280__)
inline void analogPullup(byte pin, boolean b) { 
  digitalPullup(pin+54,b); 
} 
#else
inline void analogPullup(byte pin, boolean b) { 
  digitalPullup(pin+14,b); 
}
#endif

#ifdef DEBUG
  void heart_beat(void){
    net_send("{\"hello\"}");
    Serial.println("hello");
  }
  void debug(char *msg) {
    Serial.println(msg);
  }
  void debug_(char *msg) {
    Serial.print(msg);
  }
#else
  void heart_beat(void){}
  void debug(char *msg) {}
  void debug_(char *msg) {}
#endif

void calibration_delay(void) {
  debug("calibrating sensors ");
  int s = 0;
  for (s=0; s < CALIBRATION_S; s++) {
      debug_(".");
      delay(CALIBRATION_MS);
  }
}

void init_sensor_states(void) {
sensor_states[HALL_LIGHT] = OFF; // last state of the hall light
sensor_states[HALL_PIR] = OFF; // last state of the hall PIR
sensor_states[MAIN_LIGHT] = OFF; // last state of the main room light
sensor_states[MAIN_PIR] = OFF; // last state of the main room PIR
sensor_states[WORK_LIGHT] = OFF; // last state of the work room light
sensor_states[WORK_PIR] = OFF; // last state of the work room PIR
}

boolean pirStat(int pir,int status){
  if(digitalRead(pir) == HIGH){
    lastHigh = millis();
    if (status != HIGH){
      firstHigh = millis();
    }
    status = HIGH;
  }
  if (lastHigh - firstHigh > waitForHigh){
    return ON;
  }
  if (digitalRead(pir) == LOW){       
    status = LOW;
  }
  return OFF;
}

void set_msg(void) {
  sprintf(msg,
  "{\"hall_light\":%d, \"hall_pir\":%d, \"main_light\":%d, \"main_pir\":%d, \"work_light\":%d, \"work_pir\":%d}",
  sensor_states[HALL_LIGHT], sensor_states[HALL_PIR], sensor_states[MAIN_LIGHT], sensor_states[MAIN_PIR], sensor_states[WORK_LIGHT], sensor_states[WORK_PIR]);  
}

// UDP net_send()
void net_send(char *msg)
{
  debug("net_send top");
  char *buff;
  debug("declared buff");
  sprintf(buff, "%s\n%s\n\n\0", HEADER, msg);
  debug("sprintf buff");
  debug(buff);
  Udp.sendStringMulticast(buff, targetIpAddr, port);
  debug("net_sent end");
}

void setup(void) {
  init_sensor_states();
  Serial.begin(9600);
  analogPullup(hallLight, true); // enable the 20kOhm pull-up
  analogPullup(mainLight, true);
  analogPullup(workLight, true);
  digitalPullup(mainPIR, LOW);
  digitalPullup(workPIR, LOW);
  digitalPullup(hallPIR, LOW);
  pinMode(biLed, OUTPUT); // setup built-in led for blinking
  int s;
  //calibration_delay();
  debug("connecting");
  Ethernet.begin(mac, ipAddr);
  Udp.beginMulti(localPort, ipAddr);
  debug("connected");
  net_send(HTTP_POWERED_ON);
  debug("setup end");
}

void loop(void) {
  debug("loop top");
  blink();
  // check hall light status
  value = analogRead(hallLight) < hallThreshold;
  if (value != sensor_states[HALL_LIGHT]) {
    sensor_states[HALL_LIGHT] = value;
    update = YES;
  }

  value = analogRead(mainLight) < mainThreshold;
  if (value != sensor_states[MAIN_LIGHT]) {
    sensor_states[MAIN_LIGHT] = value;
    update = YES;
  }

  value = analogRead(workLight) < workThreshold;
  if (value != sensor_states[WORK_LIGHT]) {
      sensor_states[WORK_LIGHT]  = value;
    update = YES;
  }
  // main/class room PIR
  sensor_states[MAIN_PIR]  = pirStat(mainPIR, mainPIRStatus);
  if (sensor_states[MAIN_PIR] ) update = YES;
  // work room PIR
  sensor_states[WORK_PIR] = pirStat(workPIR, workPIRStatus);
  if (sensor_states[WORK_PIR] ) update = YES;
  // hall PIR
  sensor_states[HALL_PIR] = pirStat(hallPIR, hallPIRStatus);
  if (sensor_states[HALL_PIR] ) update = YES;
  // check to see if we need to send an update anyway
  if ( (millis() - last_update) >= ttl ) {
    update = YES;
  }
  // update if needed
  if (update) {
    blinkn(2);
    set_msg();
    net_send(msg);
    last_update = millis();
    update = NO;
  }
  heart_beat();
  delay(LOOP_DELAY);  // in milliseconds
  debug("loop end");
}

