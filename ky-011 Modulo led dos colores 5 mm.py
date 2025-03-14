import time
import network
from machine import Pin
from umqtt.simple import MQTTClient

# Configuración Wi-Fi y MQTT
MQTT_BROKER = "192.168.137.210"
MQTT_TOPIC = "kapm/led/color"
MQTT_CLIENT_ID = "ky011_sensor"
WIFI_SSID = "KAREN 8870"
WIFI_PASSWORD = "e*905F06"

# Configuración del KY-011 (LED bicolor)
RED_LED_PIN = 26   # GPIO para el LED rojo
GREEN_LED_PIN = 27 # GPIO para el LED verde
red_led = Pin(RED_LED_PIN, Pin.OUT)  # Salida para el LED rojo
green_led = Pin(GREEN_LED_PIN, Pin.OUT)  # Salida para el LED verde

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
    print("🔴🟢 Alternando entre rojo y verde cada 2 segundos...")

    while True:
        # Enciende el LED rojo y apaga el verde
        red_led.on()
        green_led.off()
        client.publish(MQTT_TOPIC, "1")  # Enviar "1" para rojo
        print("📡 Rojo - Enviado '1' a MQTT")
        time.sleep(2)  # Esperar 2 segundos

        # Enciende el LED verde y apaga el rojo
        red_led.off()
        green_led.on()
        client.publish(MQTT_TOPIC, "2")  # Enviar "2" para verde
        print("📡 Verde - Enviado '2' a MQTT")
        time.sleep(2)  # Esperar 2 segundos

else:
    print("❌ No se pudo conectar a Wi-Fi.")
