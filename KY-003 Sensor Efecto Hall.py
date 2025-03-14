import time
import network
from machine import Pin
from umqtt.simple import MQTTClient

# Configuración del sensor y conexión Wi-Fi
HALL_SENSOR_PIN = 33  # Pin GPIO donde conectaste la salida del sensor
MQTT_BROKER = "192.168.137.210"
MQTT_TOPIC = "kapm/sensor/hall"
MQTT_CLIENT_ID = "hall_sensor_{}".format(int(time.time()))
WIFI_SSID = "KAREN 8870"
WIFI_PASSWORD = "e*905F06"

# Inicializar el sensor de efecto Hall como entrada digital
hall_sensor = Pin(HALL_SENSOR_PIN, Pin.IN)

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    
    for _ in range(15):
        if wlan.isconnected():
            print("Wi-Fi conectado:", wlan.ifconfig())
            return wlan
        time.sleep(1)
    
    print("No se pudo conectar a Wi-Fi")
    return None

def connect_mqtt():
    try:
        client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER)
        client.connect()
        print("Conectado a MQTT")
        return client
    except Exception as e:
        print("Error MQTT:", e)
        return None

def read_hall_sensor():
    return hall_sensor.value()  # Devuelve 1 (campo magnético detectado) o 0 (sin campo)

def publish_hall_state(client):
    if client:
        try:
            state = read_hall_sensor()
            client.publish(MQTT_TOPIC, str(state))
            print("Estado del sensor enviado:", state)
        except Exception as e:
            print("Error al publicar:", e)

# Conectar Wi-Fi y MQTT
wlan = connect_wifi()
if wlan:
    client = connect_mqtt()
    
    while True:
        if not wlan.isconnected():
            print("Wi-Fi desconectado, reconectando...")
            wlan = connect_wifi()
        
        if not client:
            print("Reintentando conexión MQTT...")
            client = connect_mqtt()
        
        publish_hall_state(client)
        time.sleep(2)  # Esperar antes de la próxima lectura
else:
    print("No se pudo conectar a Wi-Fi.")
