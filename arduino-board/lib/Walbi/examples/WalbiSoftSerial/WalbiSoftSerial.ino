#include <SoftwareSerial.h>
#include "Walbi.h"

#define SERIAL_BAUD 115200  // Baudrate to PC
#define DEBUG_BOARD_TX 10  // Arduino soft RX (connects to debug board TX)
#define DEBUG_BOARD_RX 11  // Arduino soft TX (debub board RX)

SoftwareSerial servoBusStream(DEBUG_BOARD_TX, DEBUG_BOARD_RX); // our RX is connected to the Debug Board TX;
walbi_ns::Walbi walbi(&servoBusStream, SERIAL_BAUD);

void setup()
{
    servoBusStream.begin(walbi_ns::DEBUG_BOARD_BAUD); // SoftwareSerial - connects Arduino to Debug Board serial pins (RX->TX, TX->RX, GND->GND)
}

void loop()
{
    walbi.run();
}
