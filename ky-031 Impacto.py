import time
import network
from machine import Pin
from umqtt.simple import MQTTClient

# Configuración Wi-Fi y MQTT
MQTT_BROKER = "192.168.137.210"
MQTT_TOPIC = "kapm/impact/sensor"
MQTT_CLIENT_ID = "ky031_sensor"
WIFI_SSID = "KAREN 8870"
WIFI_PASSWORD = "e*905F06"

# Configuración del sensor KY-031 (Sensor de impacto/vibración)
SENSOR_PIN = 14  # GPIO para el sensor de impacto (ajustar al pin que uses)
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
    print("💥 Esperando impacto...")

    while True:
        # Leer el estado del sensor de impacto
        impact_detected = sensor.value()  # El valor será 1 si se detecta impacto, 0 si no

        if impact_detected == 1:
            print("💥 Impacto detectado!")
            client.publish(MQTT_TOPIC, "1")  # Enviar "1" si se detecta impacto
        else:
            print("⚫ No hay impacto")
            client.publish(MQTT_TOPIC, "0")  # Enviar "0" si no se detecta impacto

        time.sleep(1)  # Esperar 1 segundo antes de la siguiente lectura

else:
    print("❌ No se pudo conectar a Wi-Fi.")
