import time
import network
from machine import Pin
from umqtt.simple import MQTTClient

# Configuración Wi-Fi y MQTT
MQTT_BROKER = "192.168.137.210"
MQTT_TOPIC = "kapm/obstaculo/sensor"
MQTT_CLIENT_ID = "ky032_sensor"
WIFI_SSID = "KAREN 8870"
WIFI_PASSWORD = "e*905F06"

# Configuración del sensor KY-032
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
    print("🚗 Esperando detección de obstáculos...")

    while True:
        # Leer el estado del sensor KY-032
        obstacle_detected = sensor.value()  # 0 = obstáculo detectado, 1 = libre

        if obstacle_detected == 0:
            print("🚧 ¡Obstáculo detectado!")
            client.publish(MQTT_TOPIC, "0")  # Enviar "0" si hay un obstáculo
        else:
            print("✅ Camino libre")
            client.publish(MQTT_TOPIC, "1")  # Enviar "1" si está libre

        time.sleep(1)  # Esperar 1 segundo antes de la siguiente lectura

else:
    print("❌ No se pudo conectar a Wi-Fi.")
