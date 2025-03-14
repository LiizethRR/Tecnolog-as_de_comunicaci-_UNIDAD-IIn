import time
import network
import random
from machine import Pin, ADC, PWM
from umqtt.simple import MQTTClient

# Configuración de pines para el LED RGB
RED_PIN = 25   # GPIO para rojo
GREEN_PIN = 26 # GPIO para verde
BLUE_PIN = 27  # GPIO para azul

# Configuración de MQTT y Wi-Fi
MQTT_BROKER = "192.168.137.210"
MQTT_TOPIC = "kapm/actuador/ledrgb"
MQTT_CLIENT_ID = "rgb_led_{}".format(int(time.time()))
WIFI_SSID = "KAREN 8870"
WIFI_PASSWORD = "e*905F06"

# Inicializar PWM para el LED RGB
red = PWM(Pin(RED_PIN), freq=1000)
green = PWM(Pin(GREEN_PIN), freq=1000)
blue = PWM(Pin(BLUE_PIN), freq=1000)

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

def set_led_color(r, g, b):
    red.duty(r)
    green.duty(g)
    blue.duty(b)

def generate_random_color():
    colors = {
        "ROJO": (1023, 0, 0, 1),
        "VERDE": (0, 1023, 0, 2),
        "AZUL": (0, 0, 1023, 3),
        "AMARILLO": (1023, 1023, 0, 4),
        "CIAN": (0, 1023, 1023, 5),
        "MAGENTA": (1023, 0, 1023, 6),
        "BLANCO": (1023, 1023, 1023, 7),
        "APAGADO": (0, 0, 0, 0)
    }
    color_name, (r, g, b, number) = random.choice(list(colors.items()))
    return color_name, r, g, b, number

def publish_color_state(client):
    if client:
        try:
            color_name, r, g, b, number = generate_random_color()
            set_led_color(r, g, b)
            client.publish(MQTT_TOPIC, str(number))
            print(f"📡 Color: {color_name}, Código: {number}")
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
        
        publish_color_state(client)
        time.sleep(2)  # Publicar cada 2 segundos
else:
    print("❌ No se pudo conectar a Wi-Fi.")
