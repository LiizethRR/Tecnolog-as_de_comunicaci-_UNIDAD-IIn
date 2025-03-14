import time
import network
from machine import Pin, ADC
from umqtt.simple import MQTTClient

SENSOR_PIN = 14
ANALOG_PIN = 34
MQTT_BROKER = "192.168.137.144"
MQTT_TOPIC = "mnml/sensor/agua-DC-3V-5V"
MQTT_CLIENT_ID = "water_sensor_{}".format(int(time.time()))
WIFI_SSID = "GUS_LAP 9476"
WIFI_PASSWORD = "@95X393b"

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    for _ in range(10):
        if wlan.isconnected():
            print("Wi-Fi conectado:", wlan.ifconfig())
            return True
        time.sleep(1)
    print("No se pudo conectar a Wi-Fi")
    return False

def connect_mqtt():
    try:
        client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER)
        client.connect()
        print("Conectado a MQTT")
        return client
    except Exception as e:
        print("Error MQTT:", e)
        return None

def publish_data(client):
    if client and Pin(SENSOR_PIN, Pin.IN).value():
        water_level = ADC(Pin(ANALOG_PIN)).read()
        client.publish(MQTT_TOPIC, str(water_level))
        print("Enviado:", water_level)

if connect_wifi():
    client = connect_mqtt()
    while True:
        publish_data(client)
        time.sleep(2)
else:
    print("No se pudo conectar a Wi-Fi.")