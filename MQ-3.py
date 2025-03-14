import time
import network
from machine import Pin, ADC
from umqtt.simple import MQTTClient

# Configuración Wi-Fi y MQTT
MQTT_BROKER = "192.168.137.210"
MQTT_TOPIC = "kapm/mq3/alcohol"
MQTT_CLIENT_ID = "mq3_sensor"
WIFI_SSID = "KAREN 8870"
WIFI_PASSWORD = "e*905F06"

# Configuración del sensor MQ3 (Pin analógico)
MQ3_PIN = 34  # GPIO para el sensor MQ3 (en el caso de un ESP32)
mq3_sensor = ADC(Pin(MQ3_PIN))  # Configura el sensor analógico

# Ajuste de rango del ADC (dependiendo de tu plataforma)
mq3_sensor.atten(ADC.ATTN_0DB)  # Rango de 0 a 1.1V (ajustable)

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
    print("📊 Leyendo valores del sensor MQ3 cada 2 segundos...")

    while True:
        # Leer el valor del sensor MQ3
        alcohol_level = mq3_sensor.read()  # Valor entre 0 y 4095 (dependiendo de la configuración ADC)

        # Normalizar el valor (si es necesario) para que tenga un rango adecuado para enviar a MQTT
        # Por ejemplo, si el rango de ADC es 0-4095 y lo mapeas a 0-100 para nivel de alcohol:
        normalized_value = (alcohol_level / 4095) * 100

        # Imprimir el nivel de alcohol detectado
        print(f"📊 Nivel de alcohol detectado: {normalized_value:.2f}%")

        # Enviar el valor a MQTT
        client.publish(MQTT_TOPIC, str(normalized_value))  # Enviar el valor como porcentaje
        print(f"📡 Enviado {normalized_value:.2f}% al tópico MQTT")

        time.sleep(2)  # Esperar 2 segundos para la siguiente lectura

else:
    print("❌ No se pudo conectar a Wi-Fi.")
