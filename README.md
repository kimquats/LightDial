# LightDial
A small appliance to control a lighting device, written in circuitpython for use with homeassistant. </h1>


LightDial has 3 components: the hardware, the firmware, and some amount of configuration in HomeAssistant. This approach does not require a dedicated integration for the hardware. All of the code is written for Circuitpython 10.2 and Homeassistant 2026.7.

## Hardware: 
1. ESP32-S2 breakout board (Adafruit Qt-Py ESP32-S2)
2. Adafruit I2C rotary encoder breakout board, with encoder
3. A Stemma QT cable to connect the two boards.

## Firmware:
1. Input handling - Logic to read the encoder & button presses.
2. MQTT messaging - Communication with your Homeassistant server via MQTT

## Homeassistant configuration
1. MQTT broker - In this case, Mosquitto running on top of Homeassistant
2. MQTT sensors - Two "sensors" that each watch a topic of your choice to capture input from the appliance.
3. Automations - These trigger on state change for each of the MQTT sensors. One to act on button presses, one to act on encoder input. In this case, to toggle lights (for button presses) and adjust brightness (for encoder turns).
