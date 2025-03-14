import time
import network
from machine import Pin
from umqtt.simple import MQTTClient

# Configuración Wi-Fi y MQTT
MQTT_BROKER = "192.168.137.210"
MQTT_TOPIC = "kapm/magnet/digital"
MQTT_CLIENT_ID = "magnet_sensor"
WIFI_SSID = "KAREN 8870"
WIFI_PASSWORD = "e*905F06"

# Configuración de la salida digital del sensor KY-024
D0_PIN = 32  # Salida digital (GPIO)
d0 = Pin(D0_PIN, Pin.IN)

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    
    for _ in range(10):
        if wlan.isconnected():
            print("✅ Wi-Fi conectado:", wlan.ifconfig())
            return wlan
        time.sleep(1)
    
    print("❌ No se pudo conectar a Wi-Fi")
    return None

def connect_mqtt():
    try:
        client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER)
        client.connect()
        print("✅ Conectado a MQTT")
        return client
    except Exception as e:
        print("❌ Error MQTT:", e)
        return None

# Conectar Wi-Fi y MQTT
wlan = connect_wifi()
client = connect_mqtt() if wlan else None

if wlan and client:
    print("🧲 Esperando detección de campo magnético...")

    last_state = d0.value()  # Estado inicial del sensor

    while True:
        state = d0.value()
        
        if state == 1 and last_state == 0:  # Solo enviar cuando se detecte el imán
            client.publish(MQTT_TOPIC, "1")  # Enviar "1" en el topic
            print("📡 Magnet detected - Enviado '1' a MQTT")
        
        last_state = state  # Actualizar estado previo
        time.sleep(0.2)  # Pequeña espera

else:
    print("❌ No se pudo conectar a Wi-Fi.")
