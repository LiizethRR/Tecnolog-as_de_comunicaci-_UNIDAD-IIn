import time
import network
from machine import Pin, ADC
from umqtt.simple import MQTTClient

# Configuración del sensor y conexión Wi-Fi
MQ2_PIN = 34  # GPIO donde conectaste la salida analógica del sensor MQ-2 (pin ADC)
MQTT_BROKER = "192.168.137.210"
MQTT_TOPIC = "kapm/sensor/mq2"
MQTT_CLIENT_ID = "mq2_sensor_{}".format(int(time.time()))
WIFI_SSID = "KAREN 8870"
WIFI_PASSWORD = "e*905F06"

# Inicializar el sensor MQ-2 como ADC (analógico)
mq2_sensor = ADC(Pin(MQ2_PIN))  # ADC en el pin configurado
mq2_sensor.atten(ADC.ATTN_11DB)  # Configuración de rango (0-3.3V en ESP32)

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

def read_mq2_sensor():
    # Leer el valor del sensor MQ-2 (escala de 0 a 4095 en ESP32)
    return mq2_sensor.read()

def publish_mq2_state(client):
    if client:
        try:
            state = read_mq2_sensor()
            client.publish(MQTT_TOPIC, str(state))
            print("📡 Estado del sensor MQ-2 enviado:", state)
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
        
        publish_mq2_state(client)
        time.sleep(2)  # Publicar cada 2 segundos
else:
    print("❌ No se pudo conectar a Wi-Fi.")
