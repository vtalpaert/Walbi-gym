#include <Leg.h>

Leg right;
Leg left;

void setup() {
  Serial.begin(9600);
  right.birth(0, A0, A1, A2, A3, A4, A5, A6);
  left.birth(1, A0, A1, A2, A3, A4, A5, A6);
}

void loop() {
  right.getAngles();
  Serial.print("Right Ankle x: ");
  Serial.println(right.ankle_x);
}
