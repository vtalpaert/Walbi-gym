#include <Arduino.h>
#include <SoftwareSerial.h>

#include "Walbi.h"

#define SERIAL_BAUD 115200  // Baudrate to PC
#define SOFT_RX 10  // Arduino soft RX (connects to debug board TX)
#define SOFT_TX 11  // Arduino soft TX (debub board RX)

Walbi::Walbi* walbi;

void setup()
{
    walbi = new Walbi::Walbi(SOFT_RX, SOFT_TX, SERIAL_BAUD);
}

void loop()
{
    walbi->get_messages_from_serial();
}
