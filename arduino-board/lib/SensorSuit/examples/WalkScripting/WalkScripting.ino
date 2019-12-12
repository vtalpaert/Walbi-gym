#include <Walbi.h>
#include <SoftwareSerial.h>

#define SERIAL_BAUD 115200  // Baudrate to PC
#define DEBUG_BOARD_TX 10  // Arduino soft RX (connects to debug board TX)
#define DEBUG_BOARD_RX 11  // Arduino soft TX (debug board RX)

SoftwareSerial servoBusStream(DEBUG_BOARD_TX, DEBUG_BOARD_RX); // pin 10 = Arduino soft RX (connects to debug board TX)
// pin 11 = Arduino soft TX (debub board RX)
walbi_ns::Walbi* walbi;
walbi_ns::State state;
walbi_ns::Action action;
walbi_ns::Action action_previous;

const int nbJoints = 10;
int pinJoint[nbJoints] = {A1, A0, A2, A3, A4, A5, A6, A7, A8, A9};

int suit_min[nbJoints] = {250, 165, 510, 550, 670, 350, 250, 730, 380, 750};
int suit_max[nbJoints] = {900, 495, 323, 265, 100, 1020, 600, 540, 620, 300};

int walbi_min[nbJoints] = {520, 380, 800, 820, 400, 380, 520, 180, 540, 650};
int walbi_max[nbJoints] = {300, 550, 530, 780, 630, 600, 700, 440, 500, 420};


void map_walbi(int val_suit, uint16_t& val_walbi, int min_suit, int max_suit, int min_walbi, int max_walbi) {
  if (val_suit == 0 || val_suit >= 1023) {
    return;
  } else if (min_suit < max_suit) {
    if (val_suit < min_suit) {
      val_suit = min_suit;
    } else if (max_suit < val_suit) {
      val_suit = max_suit;
    }
  } else if (min_suit > max_suit) {
    if (val_suit > min_suit) {
      val_suit = min_suit;
    } else if (max_suit > val_suit) {
      val_suit = max_suit;
    }
  }
  val_walbi = map(val_suit, min_suit, max_suit, min_walbi, max_walbi);
}

// Calculate based on max input size expected for one command
#define INPUT_SIZE 30
// Get next command from Serial (add 1 for final 0)
void read_values()
{
  char input[INPUT_SIZE + 1];
  byte size = Serial.readBytes(input, INPUT_SIZE);
  // Add the final 0 to end the C string
  input[size] = 0;

  // Read each command pair
  char* command = strtok(input, ":");
  char choice = *command;
  command = strtok(NULL, ":");
  int servoId = atoi(command);
  command = strtok(NULL, ":");
  int min_val = atoi(command);
  command = strtok(NULL, ":");
  int max_val = atoi(command);
  if (choice == 'w') {
    Serial.println("walbi");
    walbi_min[servoId] = min_val;
    walbi_max[servoId] = max_val;
  } else if (choice == 's') {
    Serial.println("suit");
    suit_min[servoId] = min_val;
    suit_max[servoId] = max_val;
  } else {
    Serial.println("WRONG");
  }
  Serial.println(servoId);
  Serial.println(min_val);
  Serial.println(max_val);
  Serial.println();
}

const int but_g_pin = 28;
const int gnd_g_pin = 30;
bool but_g_state = false;
int but_g;
const int but_d_pin = 29;
const int gnd_d_pin = 31;
bool but_d_state = false;
int but_d;

int mode = 1;
int max_mode = 2;
int previous_mode = 1;

int scripting = 0;
int last_scripting = 0;
const int max_scripting = 10;

int script[max_scripting][nbJoints] = {
  {425, 473, 491, 782, 515, 472, 590, 484, 527, 533},
  {445, 389, 487, 672, 499, 471, 694, 495, 642, 547},
  {267, 473, 750, 677, 603, 474, 693, 498, 642, 547},
  {267, 473, 750, 677, 700, 474, 693, 498, 642, 547},
  {459, 403, 533, 678, 607, 476, 692, 501, 643, 543},
  {410, 573, 503, 906, 477, 533, 536, 479, 403, 631},
  {410, 573, 503, 906, 477, 630, 597, 171, 406, 421},
  {410, 573, 503, 906, 477, 630, 597, 171, 406, 320},
  {396, 575, 499, 907, 478, 466, 533, 377, 419, 432},
  {396, 575, 499, 907, 478, 466, 533, 377, 419, 432},
};

#include "HX711.h"
HX711 left_foot_sensor;
HX711 right_foot_sensor;

const int weight_sensor_left_data = 34;
const int weight_sensor_left_clock = 35;
const int weight_sensor_right_data = 36;
const int weight_sensor_right_clock = 37;

void setup() {
  left_foot_sensor.begin(weight_sensor_left_data, weight_sensor_left_clock);
  delay(1000);
  right_foot_sensor.begin(weight_sensor_right_data, weight_sensor_right_clock);
  delay(1000);
  
  pinMode(but_g_pin, INPUT_PULLUP);
  pinMode(but_d_pin, INPUT_PULLUP);

  servoBusStream.begin(walbi_ns::DEBUG_BOARD_BAUD); // SoftwareSerial - connects Arduino to Debug Board serial pins (RX->TX, TX->RX, GND->GND)
  walbi = new walbi_ns::Walbi(&servoBusStream, SERIAL_BAUD, 0, 0, false);
  for (int i = 0; i < nbJoints; i++) {
    pinMode(pinJoint[i], INPUT);
    map_walbi((suit_min[i] + suit_max[i]) / 2, action.commands[i][0], suit_min[i], suit_max[i], walbi_min[i], walbi_max[i]);
  }
  Serial.println("Start");
}


void loop() {
  if (left_foot_sensor.is_ready()) {
    long reading = left_foot_sensor.read();
    Serial.print("Left HX711 reading: ");
    Serial.println(reading);
  } else {
    Serial.println("HX711 not found.");
  }

  if (right_foot_sensor.is_ready()) {
    long reading = right_foot_sensor.read();
    Serial.print("Right HX711 reading: ");
    Serial.println(reading);
  } else {
    Serial.println("HX711 not found.");
  }
  
  Serial.println();
  delay(1000);
  
  state = *walbi->getState();
  for (int ii = 0; ii < nbJoints; ii++) {
    action.commands[ii][0] = state.positions[ii];
    action.commands[ii][1] = 1000;
  }

  handle_but_g();
  handle_but_d();

  switch (mode) {
    case 1:
      break;
    case 2:
      for (int ii = 0; ii < nbJoints; ii++) {
        action.activate[ii] = true;
      }
      walbi->act(&action);
      break;
  }

  if (previous_mode != mode) {
    Serial.print("Mode\t");
    Serial.print(mode);
    if (mode == 2) {
      Serial.print("\t\tWalbi\t");
      for (int ii = 0; ii < nbJoints; ii++) {
        Serial.print(ii);
        Serial.print(" : ");
        Serial.print(state.positions[ii]);
        Serial.print("\t");
      }
    }
    Serial.println();
  }
  previous_mode = mode;
}

void handle_but_g() {
  but_g = digitalRead(but_g_pin);
  if (but_g == 0 && but_g_state == false) {
    but_g_state = true;
    mode += 1;
    if (mode > max_mode) {
      mode -= max_mode;
    }
  } else if (but_g == 1 && but_g_state == true) {
    but_g_state = false;
  }
}

void handle_but_d() {
  but_d = digitalRead(but_d_pin);
  if (but_d == 0 && but_d_state == false) {
    but_d_state = true;
    scripting += 1;
    if (scripting > max_scripting) {
      scripting -= max_scripting;
    }
    if (last_scripting != scripting) {
      for (int ii = 0; ii < nbJoints; ii++) {
        action.commands[ii][0] = script[scripting - 1][ii];
        action.commands[ii][1] = 1000;
      }
      if (scripting == max_scripting) {
        for (int ii = 5; ii < 10; ii++) {
          action.activate[ii] = false;
        }
      } else {
        for (int ii = 0; ii < nbJoints; ii++) {
          action.activate[ii] = true;
        }
      }
      walbi->act(&action);
    }
    last_scripting = scripting;
  } else if (but_d == 1 && but_d_state == true) {
    but_d_state = false;
  }
}
