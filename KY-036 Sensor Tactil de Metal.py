import time
import network
from machine import Pin
from umqtt.simple import MQTTClient

# Configuración del sensor táctil y conexión Wi-Fi
TOUCH_PIN = 32  # GPIO donde está conectado el sensor táctil de metal
MQTT_BROKER = "192.168.137.210"
MQTT_TOPIC = "kapm/sensor/touch"
MQTT_CLIENT_ID = "touch_sensor_{}".format(int(time.time()))
WIFI_SSID = "KAREN 8870"
WIFI_PASSWORD = "e*905F06"

# Inicializar el sensor táctil como entrada con pull-up interno
touch_sensor = Pin(TOUCH_PIN, Pin.IN, Pin.PULL_UP)

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    
    for _ in range(15):
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

def read_touch_sensor():
    # Leer el estado del sensor táctil (0 = tocado, 1 = no tocado)
    return touch_sensor.value()

def publish_touch_state(client):
    if client:
        try:
            state = read_touch_sensor()
            client.publish(MQTT_TOPIC, str(state))
            print(f"📡 Estado del sensor táctil enviado: {state}")
        except Exception as e:
            print("❌ Error al publicar:", e)

# Conectar Wi-Fi y MQTT
wlan = connect_wifi()
if wlan:
    client = connect_mqtt()
    
    while True:
        if not wlan.isconnected():
            print("⚠️ Wi-Fi desconectado, reconectando...")
            wlan = connect_wifi()
        
        if not client:
            print("⚠️ Reintentando conexión MQTT...")
            client = connect_mqtt()
        
        publish_touch_state(client)
        time.sleep(1)  # Publicar cada 1 segundo
else:
    print("❌ No se pudo conectar a Wi-Fi.")
