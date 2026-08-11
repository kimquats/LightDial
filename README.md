# LightDial
A small appliance to control a lighting device, written in circuitpython for use with homeassistant. This code is not plug & play but if you have the hardware, a wifi router with a 2.4 ghz network, and a homeassistant server, you should be up and running pretty quickly.

## Why? 
Mostly to teach myself how to create devices that can control other devices through homeassistant. Also because I hate voice control and touchscreens; I find them unreliable, finicky, or slow.

This is not intended to be an ongoing project. This code is inelegant and amateurish because I'm not really a software person, and I doubt I'll work more on it unless there are breaking changes in a future homeassistant update. Hopefully this means the code will be more legible to someone who is similarly green and trying to figure out how this all works. 

## Components
LightDial has 3 components: the hardware, the firmware, and some amount of configuration in HomeAssistant. This approach does not require a dedicated Homeassistant integration for the hardware. All of the code is written for Circuitpython 10.2 and Homeassistant 2026.7.

### Hardware: 
1. ESP32-S2 breakout board (Adafruit Qt-Py ESP32-S2)
2. Adafruit I2C rotary encoder breakout board, with encoder
3. A Stemma QT cable to connect the two boards.

### Firmware:
1. Input handling - Logic to read the encoder & button presses.
2. MQTT messaging - Communication with your Homeassistant server via MQTT

### Homeassistant configuration
1. MQTT broker - In this case, Mosquitto running on top of Homeassistant
2. MQTT Integration - Install the official HA MQTT integration.
2. MQTT sensors - Two "sensors" that each watch a topic of your choice to capture input from the appliance. Add these entries to configuration.yaml
3. Automations - These trigger on state change for each of the MQTT sensors. One to act on button presses, one to act on encoder input. In this case, to toggle lights (for button presses) and adjust brightness (for encoder turns). Add these entries to automation.yaml

## Control scheme

After being powered on, the device checks for user input.
### **Toggle** 
When the encoder button is pressed, the device immediately publishes an MQTT message to a dedicated topic with a command to toggle the lights without changing their brightness.

### **Brightness** 
When the encoder is rotated, a short timer is started to check for further turns of the encoder. For each tick of the encoder, the timer is reset. When the timer runs out, the board reads the encoder and publishes an MQTT message to a dedicated topic. The payload contains the percent change to increment/decrement the brightness level (in percent).

## Pain points

### Templating & config files in homeassistant
Templating is the method for computing dynamic values in homeassistant. Config files are written in YAML, with the logic blocks for templating written in Jinja2. In this case, they're how the brightness adjustment & toggle commands are passed from an MQTT message to the lighting automations. 

These gave me the most problems by far. As someone that has dipped their toes into many languages but is only familiar with Python and C, I found the syntax for templating finicky and unintuitive, and the learning curve extremely steep, doubly so because I'm not familiar with YAML. Homeassistant's documentation was hit-or-miss, and much of the reddit/forum content is outdated. Prepare for a crash course if you're learning this, and **make extensive use of the developer tools/sandboxes on your HA server.** The template editor in particular was invaluable.

### Project structure/implementation in Homeassistant 
I was not able to find much documentation that suggested an easy or general method for implementing this project in Homeassistant. In the end, I was able to cobble together a control scheme using a virtual "sensor" in homeassistant to subscribe to an MQTT topic and extract whatever info is sent in a message's payload using templating. I then set up automations to trigger when these sensors were updated, again using templating to extract the relevant command/value from the sensor state. **This solution is broadly applicable, but not universal, as templating is not supported for passing values into all automation device calls.**
