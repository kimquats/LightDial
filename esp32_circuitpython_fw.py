import board, time, random, json, wifi, adafruit_connection_manager
import adafruit_minimqtt.adafruit_minimqtt as MQTT
from adafruit_seesaw import digitalio, rotaryio, seesaw
from os import getenv

# Configure seesaw pin used to read knob button presses
# The internal pull up is enabled to prevent floating input
# i2c = board.I2C()  # uses board.SCL and board.SDA
i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller
seesaw = seesaw.Seesaw(i2c, addr=0x36)
seesaw.pin_mode(24, seesaw.INPUT_PULLUP)
button = digitalio.DigitalIO(seesaw, 24)

# Set up wifi credentials, MQTT client, topics
ssid = getenv("CIRCUITPY_WIFI_SSID")
password = getenv("CIRCUITPY_WIFI_PASSWORD")
ha_username = getenv("HA_USERNAME")
ha_key = getenv("HA_KEY")
ha_broker = getenv("HA_BROKER_IPV4")
ha_port = 1883
encoder_topic = 'home/kims_room/encoder'
button_topic = 'home/kims_room/button'
pool = adafruit_connection_manager.get_radio_socketpool(wifi.radio)
ssl_context = adafruit_connection_manager.get_radio_ssl_context(wifi.radio)
# Initialize a new MQTT Client object
mqtt_client = MQTT.MQTT(
    broker=ha_broker,
    port=ha_port,
    username=ha_username,
    password=ha_key,
    socket_pool=pool,
    ssl_context=None,
    is_ssl=False,
)

#Initialize variables for encoder logic 
initial_device_state = {'ticks': 0, 'button_pressed': 0}
device_state = initial_device_state
button_held = False
input_timer = 0.35 # Float, amount of time (in seconds) for user to input next encoder tick before they're sent
encoder_scaling_factor = 3 # Percentage change of light brightness for each encoder tick
encoder_initial_position = seesaw.set_encoder_position(0)
encoder_position = 0


def send_device_state(state, client, topic):
    # Package device state into JSON object, connect to wifi, send message, disconnect
    payload = json.dumps(state)
    if not wifi.radio.connected:
        wifi.radio.connect(ssid, password)
    # Send the sensor update
    client.connect()
    client.publish(topic, payload)
    client.disconnect()
    print(f'Sent message {state} to {topic} ')

def read_encoder(input_interval, encoder_initial_pos):
    # Start the specified timer. When the encoder ticks, reset the timer. If the timer runs out without being reset, return the number of ticks
    last_encoder_state = encoder_initial_pos
    start_time = time.monotonic()
    current_time = time.monotonic()
    while (current_time - start_time) < input_interval:
        if last_encoder_state != seesaw.encoder_position():
            start_time = time.monotonic()
            last_encoder_state = seesaw.encoder_position()
        current_time = time.monotonic()
    return -last_encoder_state * encoder_scaling_factor


while True:
    if not button.value and not button_held:
        button_held = True
        print("Button pressed")
    if button.value and button_held:
        button_held = False
        device_state['button_pressed'] = random.randint(1, 65533)
        send_device_state(device_state, mqtt_client, button_topic)
    if seesaw.encoder_position() != encoder_initial_position:
        device_state['ticks'] = read_encoder(input_timer, encoder_initial_position)
        send_device_state(device_state, mqtt_client, encoder_topic)
        print(device_state['ticks'])
        device_state['ticks'] = 0
    seesaw.set_encoder_position(0)
    encoder_initial_position = 0
    

