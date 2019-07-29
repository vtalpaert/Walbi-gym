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

The action space is a Box shaped `(10, 2)`: a target position and a given time span for each of the ten motors.

The observation space is a Box shaped `(10,)` for ten current motor positions.

A timestamp is provided in the info dictionnary.

### Arduino compilation

- Install Arduino IDE

- Copy the folders from [lib](arduino-board/lib) into your local Arduino library folder

- From the Arduino IDE, choose from `File > Examples > Walbi`

## Hardware

### Performances

Timing measurements :
- looping on STEP (computer side) ~ 150 ms
- looping on Walbi->get_state() (Arduino only) ~ 120 ms
- test with Arduino Mega (Hardware Serial Port) ~ 215ms (get state only), 225 (step)

### Buiding Walbi

Build Walbi according to [original instructions](https://create.arduino.cc/projecthub/the-inner-geek/walbi-the-walking-biped-8feacd).

### Wiring

1. Serial
    1. Connect your Arduino Serial to your computer
    1. Connect Arduino to the Debug Board by the two `DEBUG_BOARD_RX`, `DEBUG_BOARD_TX` pins
1. Bluetooth (TODO)
1. Wifi (TODO)

## Versions

1. Version `0.1.0` with `protocol-v0` is simple motor observation and action
1. Version `0.1.1` with `protocol-v1` adds time interval
1. Version `0.1.2` with `protocol-v2` removes the time interval, it is now directly the timestamp in the info dictionnary
1. Version `0.1.3` with `protocol-v3` is more straightforward with less OK messages (e.g. STEP does not send ACTION anymore). Also the responsability for a reward and termination is left to the `Env`

## Acknowledgements

1. Data sending relies on the [serial communication code](https://github.com/araffin/arduino-robust-serial)
by Antonin Raffin, as he wrote the [robust serial library](https://medium.com/@araffin/simple-and-robust-computer-arduino-serial-communication-f91b95596788)
1. The [ServoBus library](https://github.com/slandis/ServoBus) for Arduino interacts with the DebugBoard
1. Walbi was [designed](https://create.arduino.cc/projecthub/the-inner-geek/walbi-the-walking-biped-8feacd)
by [Release the Inner Geek](https://releasetheinnergeek.com/)
