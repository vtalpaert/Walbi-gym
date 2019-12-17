#include <Walbi.h>
#include <SoftwareSerial.h>

#define SERIAL_BAUD 115200  // Baudrate to PC
#define DEBUG_BOARD_TX 10  // Arduino soft RX (connects to debug board TX)
#define DEBUG_BOARD_RX 11  // Arduino soft TX (debug board RX)

SoftwareSerial servoBusStream(DEBUG_BOARD_TX, DEBUG_BOARD_RX); // pin 10 = Arduino soft RX (connects to debug board TX)
// pin 11 = Arduino soft TX (debub board RX)
walbi_ns::Walbi walbi(&servoBusStream);
walbi_ns::State state;
walbi_ns::Action action;

const int nbJoints = 10;
const int pinJoint[nbJoints] = {A1, A0, A2, A3, A4, A5, A6, A7, A8, A9};
const int ankle_left = 1;
const int hip_left = 3;
const int ankle_right = 6;
const int hip_right = 8;

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


int center_of_mass[nbJoints] = {425, 487, 491, 785, 515, 472, 618, 484, 543, 533};

const int weight_sensor_left_data = 34;
const int weight_sensor_left_clock = 35;
const int weight_sensor_right_data = 36;
const int weight_sensor_right_clock = 37;

const float scale_factor_left = -404.4138;
const float scale_factor_right = -408.3440;
const long scale_offset_left = 128666;
const long scale_offset_right = 37085;

const long left_foot_thresh = 0;
const long right_foot_thresh = 0;

unsigned long currentMillis = 0;
unsigned long lastMillis = 0;
unsigned long interval = 1000;

const int movement = 10;
bool correct_state = false;
int weight_thresh = 5;


void setup() {
  servoBusStream.begin(walbi_ns::DEBUG_BOARD_BAUD); // SoftwareSerial - connects Arduino to Debug Board serial pins (RX->TX, TX->RX, GND->GND)
  walbi.begin(SERIAL_BAUD, weight_sensor_left_data, weight_sensor_right_data, weight_sensor_left_clock, weight_sensor_right_clock, false, 500);


  for (int ii = 0; ii < nbJoints; ii++) {
    action.commands[ii][0] = center_of_mass[ii];
    action.commands[ii][1] = 500;
  }

  wait_for_input("Write a single character to put Walbi in position.");

  walbi.act(&action);

  wait_for_input("Write a single character to start center of mass research.");

  Serial.println("Start");
}


void loop() {
  currentMillis = millis();
  if (currentMillis - lastMillis >= interval)
  {
    lastMillis = currentMillis;

    state = *walbi.getState();
    if (state.correct_motor_reading) {
      Serial.print("Left weight: ");
      Serial.print((state.weight_left  - scale_offset_left)/ scale_factor_left);
      Serial.print("\t");
      Serial.print("Right weight: ");
      Serial.print((state.weight_right  - scale_offset_right)/ scale_factor_right);
      Serial.println();
      Serial.print("State: ");
      for (int ii = 0; ii < 10; ii++) {
        Serial.print(state.positions[ii]);
        Serial.print("\t");
        action.commands[ii][0] = state.positions[ii];
        action.commands[ii][1] = 250;
      }

      Serial.println();

      if (state.weight_left > state.weight_right + weight_thresh) {
        action.commands[ankle_left][0] = action.commands[ankle_left][0] - movement;
        action.commands[hip_left][0] = action.commands[hip_left][0] - movement;
        action.commands[ankle_right][0] = action.commands[ankle_right][0] + movement;
        action.commands[hip_right][0] = action.commands[hip_right][0] + movement;
      } else if (state.weight_left < state.weight_right - weight_thresh) {
        action.commands[ankle_left][0] = action.commands[ankle_left][0] + movement;
        action.commands[hip_left][0] = action.commands[hip_left][0] + movement;
        action.commands[ankle_right][0] = action.commands[ankle_right][0] - movement;
        action.commands[hip_right][0] = action.commands[hip_right][0] - movement;
      }
      Serial.print("Action: ");
      for (int ii = 0; ii < 10; ii++) {
        Serial.print(action.commands[ii][0]);
        Serial.print("\t");
      }
      Serial.println();
      Serial.println();

      walbi.act(&action);
    } else {
      Serial.println("Incorrect Motor Readings");
    }

    Serial.println();

  }
}

void wait_for_input(String msg) {
  Serial.println(msg);
  while (!Serial.available()) {
    //Do Absolutely Nothing until something is received over the serial port
  }
  Serial.read();
}
