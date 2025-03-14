import time
import network
from machine import Pin
from umqtt.simple import MQTTClient

# Configuración del sensor y conexión Wi-Fi
KY021_PIN = 14  # GPIO donde está conectado el KY-021
MQTT_BROKER = "192.168.137.210"
MQTT_TOPIC = "kapm/sensor/ky021"
MQTT_CLIENT_ID = "ky021_sensor_{}".format(int(time.time()))
WIFI_SSID = "KAREN 8870"
WIFI_PASSWORD = "e*905F06"

# Inicializar el sensor como entrada con pull-up
sensor = Pin(KY021_PIN, Pin.IN, Pin.PULL_UP)

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

def publish_sensor_state(client, state):
    if client:
        try:
            client.publish(MQTT_TOPIC, str(state))
            print("📡 Estado del sensor enviado:", state)
        except Exception as e:
            print("❌ Error al publicar:", e)

# Conectar Wi-Fi y MQTT
wlan = connect_wifi()
client = connect_mqtt() if wlan else None

if wlan and client:
    print("📡 Esperando activación del sensor KY-021...")
    last_state = sensor.value()
    
    while True:
        state = sensor.value()
        if state != last_state:  # Detectar cambio de estado
            print("🔍 Sensor activado:", state)
            publish_sensor_state(client, state)
            last_state = state
        time.sleep(0.1)  # Evitar lecturas repetidas

else:
    print("❌ No se pudo conectar a Wi-Fi.")
