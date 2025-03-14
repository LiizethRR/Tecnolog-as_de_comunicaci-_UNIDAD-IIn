import time
import network
from machine import Pin, ADC
from umqtt.simple import MQTTClient

# Configuración del sensor y conexión Wi-Fi
MQ5_PIN = 34  # GPIO donde conectaste la salida analógica del sensor MQ-5 (pin ADC)
MQTT_BROKER = "192.168.137.210"
MQTT_TOPIC = "kapm/sensor/mq5"
MQTT_CLIENT_ID = "mq5_sensor_{}".format(int(time.time()))
WIFI_SSID = "KAREN 8870"
WIFI_PASSWORD = "e*905F06"

# Inicializar el sensor MQ-5 como ADC (analogico)
mq5_sensor = ADC(Pin(MQ5_PIN))  # ADC en el pin configurado
mq5_sensor.atten(ADC.ATTN_0DB)  # Configuración de rango (0-1V)

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

def read_mq5_sensor():
    # Leer el valor del sensor MQ-5 (escala de 0 a 1023)
    return mq5_sensor.read()

def publish_mq5_state(client):
    if client:
        try:
            state = read_mq5_sensor()
            client.publish(MQTT_TOPIC, str(state))
            print("📡 Estado del sensor enviado:", state)
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
        
        publish_mq5_state(client)
        time.sleep(2)  # Publicar cada 2 segundos
else:
    print("❌ No se pudo conectar a Wi-Fi.")
