import time
import network
from machine import Pin
from umqtt.simple import MQTTClient

# Configuración Wi-Fi y MQTT
MQTT_BROKER = "192.168.137.210"
MQTT_TOPIC = "kapm/flame/sensor"
MQTT_CLIENT_ID = "ky026_sensor"
WIFI_SSID = "KAREN 8870"
WIFI_PASSWORD = "e*905F06"

# Configuración del sensor KY-026 (Sensor de flama)
SENSOR_PIN = 14  # Ajusta al pin que estás usando
sensor = Pin(SENSOR_PIN, Pin.IN)  # Configura el pin como entrada digital

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
    print("🔥 Esperando detección de flama...")

    while True:
        # Leer el estado del sensor de flama
        flame_detected = sensor.value()  # 1 = llama detectada, 0 = sin llama

        if flame_detected == 1:
            print("🔥 ¡Fuego detectado!")
            client.publish(MQTT_TOPIC, "1")  # Enviar "1" si hay fuego
        else:
            print("⚫ No hay fuego")
            client.publish(MQTT_TOPIC, "0")  # Enviar "0" si no hay fuego

        time.sleep(1)  # Esperar 1 segundo antes de la siguiente lectura

else:
    print("❌ No se pudo conectar a Wi-Fi.")
