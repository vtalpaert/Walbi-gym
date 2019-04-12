# Walbi Gym

**Walbi Gym** is a project to interact with [Walbi](https://releasetheinnergeek.com/) as an [OpenAI gym](https://gym.openai.com/) environment.


## How to use

### Gym environment

TODO


### Arduino compilation

#### 1. Using Arduino IDE

Open `arduino-board/slave/slave.ino` in your Arduino IDE.

#### 2. Using Arduino Makefile (Recommended)

This method only works with Linux/Mac Os systems: [https://github.com/sudar/Arduino-Makefile](https://github.com/sudar/Arduino-Makefile)

Install Arduino Makefile.
```
sudo apt-get install arduino-mk
```

Compile and upload the code to the Arduino (please check the board name in the Makefile):
```
cd arduino-board/
make
make upload
```

## Hardware

TODO

Explain how to connect parts

## Acknowledgments

This project relies on the serial communication code by Antonin Raffin, as he wrote the [robust serial library](https://github.com/araffin/arduino-robust-serial).

Walbi was [designed](https://create.arduino.cc/projecthub/the-inner-geek/walbi-the-walking-biped-8feacd) by [Release the Inner Geek](https://releasetheinnergeek.com/).
