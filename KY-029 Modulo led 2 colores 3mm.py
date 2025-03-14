import time
import network
from machine import Pin
from umqtt.simple import MQTTClient

# Configuración de pines y MQTT
LED_ROJO = 18  
LED_VERDE = 19  
MQTT_BROKER = "192.168.137.210"
MQTT_TOPIC = "kapm/sensor/ky011"
MQTT_CLIENT_ID = "led_sequence_{}".format(int(time.time()))
WIFI_SSID = "KAREN 8870"
WIFI_PASSWORD = "e*905F06"

# Inicializar LEDs como salida
led_rojo = Pin(LED_ROJO, Pin.OUT)
led_verde = Pin(LED_VERDE, Pin.OUT)

# Lista de estados (número, rojo, verde)
colores = [
    (1, 1, 0),  # ROJO
    (2, 0, 1),  # VERDE
    (3, 1, 1),  # AMARILLO
    (0, 0, 0)   # APAGADO
]

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

def publish_color(client, number):
    if client:
        try:
            client.publish(MQTT_TOPIC, str(number))
            print("Número enviado:", number)
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
        
        # Recorrer los estados de color
        for number, rojo, verde in colores:
            led_rojo.value(rojo)
            led_verde.value(verde)
            publish_color(client, number)
            time.sleep(2)  # Esperar 2 segundos antes de cambiar
else:
    print("No se pudo conectar a Wi-Fi.")

