import time
import network
from machine import Pin
from umqtt.simple import MQTTClient

SENSOR_PIN = 4  # Pin digital donde está conectado el KY-010
MQTT_BROKER = "192.168.137.210"
MQTT_TOPIC = "kapm/sensor/photo-interruptor"
MQTT_CLIENT_ID = "photo_sensor_{}".format(int(time.time()))
WIFI_SSID = "KAREN 8870"
WIFI_PASSWORD = "e*905F06"

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

def publish_data(client, sensor):
    if client:
        state = sensor.value()  # 0 si el haz está interrumpido, 1 si no lo está
        client.publish(MQTT_TOPIC, str(state))
        print("Enviado:", state)

if connect_wifi():
    client = connect_mqtt()
    sensor = Pin(SENSOR_PIN, Pin.IN)  # Configurar el KY-010 como entrada digital
    while True:
        publish_data(client, sensor)
        time.sleep(1)  # Ajusta el tiempo de muestreo según sea necesario
else:
    print("No se pudo conectar a Wi-Fi.")
