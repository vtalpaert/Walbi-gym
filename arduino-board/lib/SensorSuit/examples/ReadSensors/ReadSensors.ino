#include <SensorSuit.h>

Leg right;
Leg left;
SensorSuit suit_n01;

void setup() {
  Serial.begin(9600);
  right.build(0, A0, A1, A2, A3, A4, A5, A6);
  left.build(1, A0, A1, A2, A3, A4, A5, A6);
  suit_n01.build(right, left);
}

void loop() {
  suit_n01.getAngles();
}
