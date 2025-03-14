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
mqtt_topic = "kapm/temperatura/analoga"  # Tema donde se publicarán los datos
mqtt_client_id = "sensor_temp_{}".format(int(time.time()))  # ID único

# Configuración del sensor KY-013
TEMP_PIN = 34  # Pin ADC del sensor KY-013
sensor_temp = ADC(Pin(TEMP_PIN))
sensor_temp.atten(ADC.ATTN_11DB)  # Ajuste para leer hasta 3.3V

# 📌 Función para leer la temperatura en °C (Mejor aproximación)
def read_temperature():
    raw_value = sensor_temp.read()  # Leer ADC (0-4095)
    voltage = raw_value * (3.3 / 4095)  # Convertir a voltaje (0-3.3V)

    temperature = (voltage - 0.5) * 100  # Ajuste según el rango de 0-3.3V
    print("Temperatura calculada:", temperature)  # Diagnóstico

    return round(temperature, 2)  # Redondear a 2 decimales

    return round(temperature, 2)  # Redondear a 2 decimales

# 📡 Conectar Wi-Fi
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    if not wlan.isconnected():
        print('Conectando a la red Wi-Fi...')
        wlan.connect(wifi_ssid, wifi_password)
        
        timeout = 10
        while not wlan.isconnected() and timeout > 0:
            time.sleep(1)
            timeout -= 1

    if wlan.isconnected():
        print('Conexión Wi-Fi exitosa:', wlan.ifconfig())
    else:
        print("Error: No se pudo conectar a Wi-Fi")
        return False
    return True

# 📡 Conectar a MQTT
def connect_mqtt():
    try:
        client = MQTTClient(mqtt_client_id, mqtt_broker, mqtt_port)
        client.connect()
        print("Conectado al broker MQTT")
        return client
    except Exception as e:
        print("Error al conectar al broker MQTT:", e)
        return None

# 📤 Enviar datos de temperatura por MQTT
def publish_data(client, last_value):
    if client is None:
        print("MQTT no está conectado")
        return last_value

    try:
        temperature = read_temperature()  # Leer temperatura en °C

        if abs(temperature - last_value) > 0.5:  # Solo enviar si cambia más de 0.5°C
            client.publish(mqtt_topic, str(temperature))
            print("Temperatura enviada:", temperature, "°C")
            return temperature
        else:
            print("Temperatura sin cambios, no se envía")
            return last_value
    except Exception as e:
        print("Error al leer la temperatura:", e)
        return last_value

# 🔄 Bucle principal
if connect_wifi():
    client = connect_mqtt()
    last_value = -100  # Última temperatura enviada

    while True:
        last_value = publish_data(client, last_value)
        time.sleep(5)  # Leer cada 5 segundos
else:
    print("No se pudo establecer conexión Wi-Fi. Reinicia el dispositivo.")
