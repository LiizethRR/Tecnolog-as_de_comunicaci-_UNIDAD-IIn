import time
import network
from machine import Pin
from umqtt.simple import MQTTClient

# Configuración Wi-Fi y MQTT
MQTT_BROKER = "192.168.137.210"
MQTT_TOPIC = "kapm/line/sensor"
MQTT_CLIENT_ID = "ky033_sensor"
WIFI_SSID = "KAREN 8870"
WIFI_PASSWORD = "e*905F06"

# Configuración del sensor KY-033
SENSOR_PIN = 14  # GPIO donde está conectado el sensor
sensor = Pin(SENSOR_PIN, Pin.IN)  # Configurar como entrada digital

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
    print("🚗 Esperando detección de línea...")

    while True:
        # Leer el estado del sensor KY-033
        line_detected = sensor.value()  # 0 = línea oscura, 1 = superficie clara

        if line_detected == 0:
            print("⬛ Línea detectada")
            client.publish(MQTT_TOPIC, "0")  # Enviar "0" si detecta línea oscura
        else:
            print("⬜ Superficie clara")
            client.publish(MQTT_TOPIC, "1")  # Enviar "1" si detecta superficie clara

        time.sleep(0.5)  # Ajusta el tiempo de muestreo según sea necesario

else:
    print("❌ No se pudo conectar a Wi-Fi.")
