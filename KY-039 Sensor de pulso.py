import time
import network
from machine import Pin
from umqtt.simple import MQTTClient

# Configuración del sensor de pulso y conexión Wi-Fi
PULSE_PIN = 33  # GPIO donde está conectado el sensor de pulso
MQTT_BROKER = "192.168.137.210"
MQTT_TOPIC = "kapm/sensor/pulse"
MQTT_CLIENT_ID = "pulse_sensor_{}".format(int(time.time()))
WIFI_SSID = "KAREN 8870"
WIFI_PASSWORD = "e*905F06"

# Inicializar el sensor de pulso como entrada digital
pulse_sensor = Pin(PULSE_PIN, Pin.IN)

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

def read_pulse_sensor(duration=2):
    count = 0
    start_time = time.time()
    
    while time.time() - start_time < duration:
        if pulse_sensor.value() == 1:  # Detecta un pulso
            count += 1
            time.sleep(0.05)  # Evitar conteos múltiples por rebote
    
    bpm = count * 6  # Convertir pulsos en BPM (latidos por minuto)
    return bpm

def publish_pulse_state(client):
    if client:
        try:
            bpm = read_pulse_sensor()
            client.publish(MQTT_TOPIC, str(bpm))
            print(f"📡 BPM enviados: {bpm}")
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
        
        publish_pulse_state(client)
        time.sleep(2)  # Publicar cada 10 segundos
else:
    print("❌ No se pudo conectar a Wi-Fi.")
