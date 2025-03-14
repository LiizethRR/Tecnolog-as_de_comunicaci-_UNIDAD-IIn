import time
import network
from machine import Pin, ADC
from umqtt.simple import MQTTClient

# Configuración del sensor y conexión Wi-Fi
LM35_PIN = 33  # Pin ADC donde conectaste VOUT del LM35
MQTT_BROKER = "192.168.137.210"
MQTT_TOPIC = "kapm/sensor/temperaturaa"
MQTT_CLIENT_ID = "lm35_sensor_{}".format(int(time.time()))
WIFI_SSID = "KAREN 8870"
WIFI_PASSWORD = "e*905F06"

# Inicializar ADC
adc = ADC(Pin(LM35_PIN))
adc.atten(ADC.ATTN_11DB)  # Permite medir de 0V a 3.3V

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

def read_temperature():
    raw_value = adc.read()  # Leer valor ADC (0-4095)
    voltage = raw_value * (3.3 / 4095)  # Convertir a voltaje
    temperature = voltage * 100  # LM35 da 10mV/°C, así que multiplicamos por 100
    return int(temperature)  # Convertimos a entero

def publish_temperature(client):
    if client:
        try:
            temperature = read_temperature()
            client.publish(MQTT_TOPIC, str(temperature))
            print("Temperatura enviada:", temperature, "°C")
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
        
        publish_temperature(client)
        time.sleep(2)  # Esperar antes de la próxima lectura
else:
    print("No se pudo conectar a Wi-Fi.")
