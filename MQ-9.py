import time
import network
from machine import Pin, ADC
from umqtt.simple import MQTTClient

# 🔌 Configuración de pines y conexión Wi-Fi
MQ9_PIN = 34  # GPIO donde conectaste la salida analógica del MQ-9
MQTT_BROKER = "192.168.137.210"
MQTT_TOPIC = "kapm/sensor/mq9"
MQTT_CLIENT_ID = "mq9_sensor_{}".format(int(time.time()))
WIFI_SSID = "KAREN 8870"
WIFI_PASSWORD = "e*905F06"

# 📡 Inicializar el sensor MQ-9 como ADC (entrada analógica)
mq9_sensor = ADC(Pin(MQ9_PIN))
mq9_sensor.atten(ADC.ATTN_11DB)  # Rango de 0 a 3.3V en ESP32

def connect_wifi():
    """ Conecta el ESP32 a la red Wi-Fi """
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)

    for _ in range(15):  # Esperar hasta 15 segundos
        if wlan.isconnected():
            print("✅ Wi-Fi conectado:", wlan.ifconfig())
            return wlan
        time.sleep(1)
    
    print("❌ No se pudo conectar a Wi-Fi")
    return None

def connect_mqtt():
    """ Conecta el ESP32 al broker MQTT """
    try:
        client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER)
        client.connect()
        print("✅ Conectado a MQTT")
        return client
    except Exception as e:
        print("❌ Error al conectar MQTT:", e)
        return None

def read_mq9_sensor():
    """ Lee el valor del sensor MQ-9 """
    return mq9_sensor.read()

def publish_mq9_state(client):
    """ Publica el estado del sensor MQ-9 en MQTT """
    if client:
        try:
            state = read_mq9_sensor()
            client.publish(MQTT_TOPIC, str(state))
            print("📡 Valor MQ-9 enviado:", state)
        except Exception as e:
            print("❌ Error al publicar:", e)

# 🔗 Conectar Wi-Fi y MQTT
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
        
        publish_mq9_state(client)
        time.sleep(2)  # Publicar cada 2 segundos
else:
    print("❌ No se pudo conectar a Wi-Fi.")
