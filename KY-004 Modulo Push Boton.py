import time
import network
from machine import Pin
from umqtt.simple import MQTTClient

# Configuración del botón y MQTT
BUTTON_PIN = 4  # Pin GPIO donde está conectado el botón
MQTT_BROKER = "192.168.137.210"
MQTT_TOPIC = "kapm/sensor/boton"
MQTT_CLIENT_ID = "button_sensor_{}".format(int(time.time()))
WIFI_SSID = "KAREN 8870"
WIFI_PASSWORD = "e*905F06"

# Inicializar botón con resistencia pull-up
button = Pin(BUTTON_PIN, Pin.IN, Pin.PULL_UP)

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

def publish_button_state(client):
    if client:
        try:
            state = button.value()  # Leer estado del botón (1 = no presionado, 0 = presionado)
            client.publish(MQTT_TOPIC, str(state))
            print("Estado del botón enviado:", "Presionado" if state == 0 else "No presionado")
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
        
        publish_button_state(client)
        time.sleep(1)  # Enviar estado cada segundo
else:
    print("No se pudo conectar a Wi-Fi.")
