import time
import network
from machine import Pin
from umqtt.simple import MQTTClient

# Configuración del sensor y conexión Wi-Fi
KY022_PIN = 14  # GPIO donde está conectado el KY-022
MQTT_BROKER = "192.168.137.210"
MQTT_TOPIC = "kapm/sensor/ky022"
MQTT_CLIENT_ID = "ky022_sensor_{}".format(int(time.time()))
WIFI_SSID = "KAREN 8870"
WIFI_PASSWORD = "e*905F06"

# Inicializar el sensor como entrada
sensor_ir = Pin(KY022_PIN, Pin.IN)

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

def publish_ir_signal(client, signal):
    if client:
        try:
            client.publish(MQTT_TOPIC, str(signal))
            print("📡 Estado IR enviado:", signal)
        except Exception as e:
            print("❌ Error al publicar:", e)

# Conectar Wi-Fi y MQTT
wlan = connect_wifi()
client = connect_mqtt() if wlan else None

if wlan and client:
    print("📡 Esperando señales IR en el sensor KY-022...")
    
    last_state = None  # Variable para evitar publicaciones repetidas

    while True:
        current_state = 1 if sensor_ir.value() == 0 else 0  # 1 si recibe señal, 0 si no
        
        if current_state != last_state:  # Solo enviar si hay un cambio de estado
            print(f"🔍 Señal IR: {current_state}")
            publish_ir_signal(client, current_state)
            last_state = current_state

        time.sleep(0.2)  # Pequeña espera para evitar lecturas repetidas

else:
    print("❌ No se pudo conectar a Wi-Fi.")
