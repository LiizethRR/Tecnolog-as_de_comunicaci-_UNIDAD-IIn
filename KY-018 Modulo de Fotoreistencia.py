import network
import time
from machine import Pin, ADC
from umqtt.simple import MQTTClient

# Configuración Wi-Fi
wifi_ssid = "KAREN 8870"  # Cambia por tu SSID
wifi_password = "e*905F06"  # Cambia por tu contraseña

# Configuración MQTT
mqtt_broker = "192.168.137.210"  # IP del broker MQTT
mqtt_port = 1883 
mqtt_topic = "kapm/luz"  # Tema donde se publicarán los datos
mqtt_client_id = "sensor_{}".format(int(time.time()))  # ID único

# Configuración de la fotoresistencia
LDR_PIN = 34  # Pin ADC de la fotoresistencia (ESP32 usa 32-39 para ADC)

ldr = ADC(Pin(LDR_PIN))  # Fotoresistencia como entrada analógica
ldr.atten(ADC.ATTN_11DB)  # Ajuste para leer hasta 3.3V

# Conexión Wi-Fi con manejo de errores
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    if not wlan.isconnected():
        print('Conectando a la red Wi-Fi...')
        wlan.connect(wifi_ssid, wifi_password)
        
        timeout = 10  # Esperar hasta 10 segundos para la conexión
        while not wlan.isconnected() and timeout > 0:
            time.sleep(1)
            timeout -= 1

    if wlan.isconnected():
        print('Conexión Wi-Fi exitosa:', wlan.ifconfig())
    else:
        print("Error: No se pudo conectar a Wi-Fi")
        return False
    return True

# Conexión MQTT con manejo de errores
def connect_mqtt():
    try:
        client = MQTTClient(mqtt_client_id, mqtt_broker, mqtt_port)
        client.connect()
        print("Conectado al broker MQTT")
        return client
    except Exception as e:
        print("Error al conectar al broker MQTT:", e)
        return None

# Enviar datos de la fotoresistencia por MQTT cada 5 segundos
def publish_data(client):
    if client is None:
        print("MQTT no está conectado")
        return

    try:
        light_level = ldr.read()  # Leer el valor analógico (0-4095 en ESP32)
        client.publish(mqtt_topic, str(light_level))  # Enviar como cadena
        print("Nivel de luz enviado:", light_level)
    except Exception as e:
        print("Error al leer la fotoresistencia:", e)

# Main
if connect_wifi():  # Conectar a Wi-Fi
    client = connect_mqtt()  # Conectar a MQTT

    while True:
        publish_data(client)  # Enviar el nivel de luz
        time.sleep(5)  # Esperar 5 segundos antes del próximo envío
else:
    print("No se pudo establecer conexión Wi-Fi. Reinicia el dispositivo.")
