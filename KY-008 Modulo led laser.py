import time
import network
from machine import Pin
from umqtt.simple import MQTTClient

# Definir el pin de control del láser
LASER_PIN = 18  # Pin de control del láser
MQTT_BROKER = "192.168.137.210"
MQTT_TOPIC = "kapm/sensor/laser"
MQTT_CLIENT_ID = "laser_sensor_{}".format(int(time.time()))
WIFI_SSID = "KAREN 8870"
WIFI_PASSWORD = "e*905F06"

# Inicializar el pin del láser como salida
laser = Pin(LASER_PIN, Pin.OUT)

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

def publish_laser_state(client, state):
    if client:
        try:
            client.publish(MQTT_TOPIC, str(state))
            print("Estado del láser enviado:", state)
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
        
        # Encender el láser
        laser.value(1)  # Enciende el láser
        publish_laser_state(client, 1)  # Publicar '1' cuando el láser esté encendido
        time.sleep(2)  # El láser se mantiene encendido por 2 segundos
        
        # Apagar el láser
        laser.value(0)  # Apaga el láser
        publish_laser_state(client, 0)  # Publicar '0' cuando el láser esté apagado
        time.sleep(2)  # El láser se mantiene apagado por 2 segundos
else:
    print("No se pudo conectar a Wi-Fi.")

