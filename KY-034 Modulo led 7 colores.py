import time
import network
import random
from machine import Pin, PWM
from umqtt.simple import MQTTClient

# Configuración Wi-Fi y MQTT
MQTT_BROKER = "192.168.137.210"
MQTT_TOPIC = "kapm/led/color7colores"
MQTT_CLIENT_ID = "ky029_led"
WIFI_SSID = "KAREN 8870"
WIFI_PASSWORD = "e*905F06"

# Pines del KY-029
PIN_ROJO = 25  # GPIO para LED rojo
PIN_AZUL = 26  # GPIO para LED azul

# Configuración PWM para controlar la intensidad de los LEDs
rojo = PWM(Pin(PIN_ROJO), freq=1000)
azul = PWM(Pin(PIN_AZUL), freq=1000)

# Diccionario de colores predefinidos
colores = [
    ("rojo", (1023, 0), 1),
    ("azul", (0, 1023), 2),
    ("morado", (1023, 1023), 3),
    ("rosa", (800, 600), 4),
    ("violeta", (600, 900), 5),
    ("lila", (400, 700), 6),
    ("apagado", (0, 0), 0)
]

def set_color(r, b):
    """Configura la intensidad de los LEDs"""
    rojo.duty(r)
    azul.duty(b)

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
    print("🎨 Generando colores aleatorios...")

    while True:
        # Seleccionar un color aleatorio
        nombre, (r, b), numero = random.choice(colores)

        # Aplicar el color en el LED
        set_color(r, b)

        # Mostrar y enviar el color
        print(f"🎨 Color: {nombre} (#{numero})")
        client.publish(MQTT_TOPIC, str(numero))  # Enviar número a MQTT

        time.sleep(3)  # Cambia de color cada 3 segundos

else:
    print("❌ No se pudo conectar a Wi-Fi.")
