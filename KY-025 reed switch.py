import time
import network
from machine import Pin
from umqtt.simple import MQTTClient

# Configuración Wi-Fi y MQTT
MQTT_BROKER = "192.168.137.210"
MQTT_TOPIC = "kapm/reed/Switch"
MQTT_CLIENT_ID = "reed_switch"
WIFI_SSID = "KAREN 8870"
WIFI_PASSWORD = "e*905F06"

# Configuración del KY-025 (Salida digital)
D0_PIN = 32  # GPIO para el reed switch
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
        
        if state != last_state:  # Solo enviar si cambia el estado
            client.publish(MQTT_TOPIC, str(state))  # Enviar "1" o "0"
            print(f"📡 Estado cambiado: {state} - Enviado a MQTT")
        
        last_state = state  # Actualizar estado previo
        time.sleep(0.2)  # Pequeña espera

else:
    print("❌ No se pudo conectar a Wi-Fi.")
