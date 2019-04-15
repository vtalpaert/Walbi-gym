#ifndef PARAMETERS_H
#define PARAMETERS_H

#define SERIAL_BAUD 115200  // Baudrate to PC
#define SOFTWARE_SERIAL_BAUD 115200  // Baudrate to DebugBoard
#define SOFT_RX 10  // Arduino soft RX (connects to debug board TX)
#define SOFT_TX 11  // Arduino soft TX (debub board RX)

#define MOTOR_NB 10
const uint8_t MOTOR_IDS[MOTOR_NB] = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9};

#endif
