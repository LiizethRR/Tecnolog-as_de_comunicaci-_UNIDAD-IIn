import time
import network
from machine import Pin, ADC
from umqtt.simple import MQTTClient

# Configuración Wi-Fi y MQTT
MQTT_BROKER = "192.168.137.210"
MQTT_TOPIC = "kapm/hallanalogo/sensor"
MQTT_CLIENT_ID = "ky035_sensor"
WIFI_SSID = "KAREN 8870"
WIFI_PASSWORD = "e*905F06"

# Configuración del sensor KY-035
SENSOR_PIN = 35  # GPIO donde está conectado el sensor (ESP32)
sensor = ADC(Pin(SENSOR_PIN))  # Configurar como entrada analógica
sensor.atten(ADC.ATTN_11DB)  # Configuración para leer hasta 3.3V en ESP32

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

    while True:
        # Leer el valor analógico del sensor KY-035
        hall_value = sensor.read()  # Valor entre 0 y 4095 (ESP32)

        print(f"🧲 Intensidad del campo: {hall_value}")
        client.publish(MQTT_TOPIC, str(hall_value))  # Enviar valor por MQTT

        time.sleep(1)  # Esperar 1 segundo antes de la siguiente lectura

else:
    print("❌ No se pudo conectar a Wi-Fi.")
