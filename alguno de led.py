import time
import network
from machine import Pin, PWM
from umqtt.simple import MQTTClient

# Pines PWM del KY-016 (ajusta según tu conexión)
RED_PIN = 15
GREEN_PIN = 4
BLUE_PIN = 2

# Configuración MQTT
MQTT_BROKER = "192.168.137.210"
MQTT_TOPIC = "kapm/sensor/color"
MQTT_CLIENT_ID = "color_sensor_{}".format(int(time.time()))
WIFI_SSID = "KAREN 8870"
WIFI_PASSWORD = "e*905F06"

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    for _ in range(10):
        if wlan.isconnected():
            print("Wi-Fi conectado:", wlan.ifconfig())
            return True
        time.sleep(1)
    print("No se pudo conectar a Wi-Fi")
    return False

def connect_mqtt():
    try:
        client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER)
        client.connect()
        print("Conectado a MQTT")
        return client
    except Exception as e:
        print("Error MQTT:", e)
        return None

def generate_color_sequence():
    """Cambia entre Rojo (1), Verde (0) y Azul (2)"""
    while True:
        yield (1, 1023, 0, 0)  # Rojo
        yield (0, 0, 1023, 0)  # Verde
        yield (2, 0, 0, 1023)  # Azul

color_generator = generate_color_sequence()

def set_color():
    """Configura el LED en Rojo, Verde o Azul y devuelve el número correspondiente"""
    color_code, r, g, b = next(color_generator)
    pwm_red.duty(r)
    pwm_green.duty(g)
    pwm_blue.duty(b)
    return color_code

def publish_data(client):
    if client:
        color_code = set_color()
        client.publish(MQTT_TOPIC, str(color_code))
        print("Enviado:", color_code)

if connect_wifi():
    client = connect_mqtt()

    # Configurar los pines como PWM
    pwm_red = PWM(Pin(RED_PIN), freq=500)
    pwm_green = PWM(Pin(GREEN_PIN), freq=500)
    pwm_blue = PWM(Pin(BLUE_PIN), freq=500)

    while True:
        publish_data(client)
        time.sleep(2)  # Cambia de color cada 2 segundos
else:
    print("No se pudo conectar a Wi-Fi.")

