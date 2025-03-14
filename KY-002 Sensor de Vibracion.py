import time
import network
from machine import Pin
from umqtt.simple import MQTTClient
import dht

# Configuración
DHT_PIN = 4  # Pin donde está conectado el DHT11
MQTT_BROKER = "192.168.137.210"
MQTT_TOPIC = "kapm/sensor/temperaturaa"
MQTT_CLIENT_ID = "dht11_sensor_{}".format(int(time.time()))
WIFI_SSID = "KAREN 8870"
WIFI_PASSWORD = "e*905F06"

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

def publish_temperature(client, sensor):
    if client:
        try:
            sensor.measure()  # Tomar lectura del DHT11
            temperature = sensor.temperature()  # Obtener la temperatura en entero
            client.publish(MQTT_TOPIC, str(temperature))
            print("Temperatura enviada:", temperature)
        except Exception as e:
            print("Error al publicar:", e)

# Inicio del programa
wlan = connect_wifi()
if wlan:
    client = connect_mqtt()
    sensor = dht.DHT11(Pin(DHT_PIN))  # Inicializar sensor DHT11
    
    while True:
        if not wlan.isconnected():
            print("Wi-Fi desconectado, reconectando...")
            wlan = connect_wifi()
        
        if not client:
            print("Reintentando conexión MQTT...")
            client = connect_mqtt()
        
        publish_temperature(client, sensor)
        time.sleep(2)  # Espera de 2 segundos entre lecturas
else:
    print("No se pudo conectar a Wi-Fi.")
