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
 */
 
#include <stdio.h>

//define USE_PIR
#define DEBUG
#define YES true
#define NO false
#define ON true
#define OFF false

 
// constants 
const int hallLight = 0;
const int hallThreshold = 128; // threshold for on/off
const int mainLight = 1;
const int mainThreshold = 32;
const int workLight = 2;
const int workThreshold = 128;
const int mainPIR = 11;
const int workPIR = 12;
const int hallPIR = 13; // CHECK ME
const int ttl = 5000; // minimum frequency for data updates in ms
const int calibrationTime = 30; // PIR calibration time in seconds
const int waitForHigh = 10; // cycles to wait before considering the high value motion

// variables
boolean value = OFF; // variable for each sensor's value
boolean update = NO; // do i need to update?
int timeout = 0; // last time the data was updated
unsigned long lastHigh = 0;
unsigned long firstHigh = 0;

// light sensor states
boolean hallLightState = OFF; // last state of the hall light
boolean mainLightState = OFF; // last state of the main room light
boolean workLightState = OFF; // last state of the work room light

// PIR sensor states
boolean mainPIRState = OFF; // last state of the main room PIR
int mainPIRStatus = LOW;
boolean workPIRState = OFF; // last state of the work room PIR
int workPIRStatus = LOW;
boolean hallPIRState = OFF; // last state of the hall PIR
int hallPIRStatus = LOW;


// info storage
char json[256]; // json string
unsigned long last = 0; // milliseconds of last update

// shortcuts
inline void digitalPullup(byte pin, boolean b) {  pinMode(pin, INPUT);  digitalWrite(pin, b?HIGH:LOW); }
#if defined(__AVR_ATmega1280__)
inline void analogPullup(byte pin, boolean b) { digitalPullup(pin+54,b); } 
#else
inline void analogPullup(byte pin, boolean b) { digitalPullup(pin+14,b); }
#endif

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

void setup() {

	Serial.begin(9600);

	analogPullup(hallLight, true); // enable the 20kOhm pull-up

	analogPullup(mainLight, true);

	analogPullup(workLight, true);

	digitalPullup(mainPIR, LOW);

	digitalPullup(workPIR, LOW);

	digitalPullup(hallPIR, LOW);

	int s;
	for(s=0;s <= calibrationTime;s++){
		Serial.println("calibrating sensors ...");
		delay(980);
	}
}

void loop() {
	
  // check hall light status
  value = analogRead(hallLight) < hallThreshold;
  if (value != hallLightState) {
    hallLightState = value;
    update = YES;
  }
  
  value = analogRead(mainLight) < mainThreshold;
  if (value != mainLightState) {
    mainLightState = value;
    update = YES;
  }
  
  value = analogRead(workLight) < workThreshold;
  if (value != workLightState) {
    workLightState = value;
    update = YES;
  }

  mainPIRState = pirStat(mainPIR, mainPIRStatus);

  if (mainPIRState) update = YES;

  workPIRState = pirStat(workPIR, workPIRStatus);

  if (workPIRState) update = YES;

  hallPIRState = pirStat(hallPIR, hallPIRStatus);

  if (hallPIRState) update = YES;

  // check to see if we need to send an update anyway
  if ( (millis() - last) >= ttl ) {
    update = YES;
  }

  if (update) {
    sprintf(json, "{\"hall_light\":%d, \"main_light\":%d, \"work_light\":%d, \"main_pir\":%d, \"work_pir\":%d,\"hall_pir\":%d}", hallLightState, mainLightState, workLightState, mainPIRState, workPIRState, hallPIRState);
    Serial.println(json);
    last = millis();
    update = NO;
  }
 
  delay(100);  // .1 second delay
}
