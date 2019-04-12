#ifndef PARAMETERS_H
#define PARAMETERS_H

#define SERIAL_BAUD 115200  // Baudrate
#define SOFT_RX 10  // Arduino soft RX (connects to debug board TX)
#define SOFT_TX 11  // Arduino soft TX (debub board RX)

//
// This code by LewanSoul to control LX16-A serial servos (not provided as library)
//

#define GET_LOW_BYTE(A) (byte)((A))
#define GET_HIGH_BYTE(A) (byte)((A) >> 8)
#define BYTE_TO_HW(A, B) ((((unsigned int)(A)) << 8) | (byte)(B))
#define LOBOT_SERVO_FRAME_HEADER          0x55
#define LOBOT_SERVO_MOVE_TIME_WRITE       1

#endif
