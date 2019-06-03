# Walbi Gym

**Walbi Gym** is a project to interact with [Walbi](https://releasetheinnergeek.com/) as an [OpenAI gym](https://gym.openai.com/) environment.


## How to use

### Install the Python3 module

```bash
python3 setup.py
```

### Gym environment

You may create a Walbi Gym environment as usual.

```python
import gym
import walbi_gym  # will register env
env = gym.make('Walbi-v0')
```

### Arduino compilation

Arduino Makefile only works with Linux/Mac Os systems: [https://github.com/sudar/Arduino-Makefile](https://github.com/sudar/Arduino-Makefile)

Install Arduino Makefile:

```bash
sudo apt-get install arduino-mk
```

Compile and upload the code to the Arduino (please check the board name in the Makefile):

```bash
cd arduino-board/
make
make upload
```

## Hardware

TODO

Explain how to connect parts

## Acknowledgments

This project relies on the [serial communication code](https://github.com/araffin/arduino-robust-serial)
by Antonin Raffin, as he wrote the [robust serial library](https://medium.com/@araffin/simple-and-robust-computer-arduino-serial-communication-f91b95596788).

Walbi was [designed](https://create.arduino.cc/projecthub/the-inner-geek/walbi-the-walking-biped-8feacd)
by [Release the Inner Geek](https://releasetheinnergeek.com/).
