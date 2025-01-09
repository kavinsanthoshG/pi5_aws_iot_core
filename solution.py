import time
import paho.mqtt.client as mqtt
import ssl
from gpiozero import Button
#since the gpizero does not have a class for sound sensor, and by considering that the behaviour of both the button and sound sensor is same,
# the button is used as a substitution.
# Set up the sound sensor (using a Button object for simplicity)
SOUND_SENSOR_PIN = 4  # GPIO pin number (adjust as needed)
sound_sensor = Button(SOUND_SENSOR_PIN, pull_up=True)

# Define the MQTT callback for successful connection
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected successfully to AWS IoT Core")
    else:
        print(f"Connection failed with code {rc}")

# Initialize the MQTT client
client = mqtt.Client()
client.on_connect = on_connect

# Set TLS/SSL parameters for AWS IoT Core connection
#Path to your File
client.tls_set(
    ca_certs='./rootCA.pem',
    certfile='./0f0dd4e9bc25711c72adaf1bdaa45913e3339518069acd2d8188d2a7f0cc6f8b-certificate.pem.crt',
    keyfile='./0f0dd4e9bc25711c72adaf1bdaa45913e3339518069acd2d8188d2a7f0cc6f8b-private.pem.key',
    tls_version=ssl.PROTOCOL_TLSv1_2
)
client.tls_insecure_set(True)

# Connect to AWS IoT Core
client.connect("YOUR ENDPOINT", 8883, 60)

# Function to detect sound and send data to AWS IoT Core
def send_sound_data():
    while True:
        # Detect sound status from the sensor
        if sound_sensor.is_pressed:
            sound_detected = True
        else:
            sound_detected = False
        
        # Prepare the payload to send
        payload = {
            "sound_detected": sound_detected,
            "timestamp": time.time()
        }
        
        # Publish the payload to AWS IoT Core
        client.publish("device/sound_data", payload=str(payload), qos=0, retain=False)
        print(f"Sound data sent: {payload}")
        
        time.sleep(5)  # Delay before next check

# Start the MQTT loop and send sound sensor data
try:
    # Wait for connection to AWS IoT Core and then send sound data
    client.loop_start()  # Start the loop in background
    send_sound_data()
except KeyboardInterrupt:
    print("Stopped by user")
finally:
    client.loop_stop()
    client.disconnect()
