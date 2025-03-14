import time
import network
from machine import Pin, ADC
from umqtt.simple import MQTTClient

# Configuración Wi-Fi y MQTT
MQTT_BROKER = "192.168.137.210"
MQTT_TOPIC = "kapm/joystick"
MQTT_CLIENT_ID = "joystick_{}".format(int(time.time()))
WIFI_SSID = "KAREN 8870"
WIFI_PASSWORD = "e*905F06"

# Pines del joystick
VRX_PIN = 34  # Eje X (ADC1)
VRY_PIN = 35  # Eje Y (ADC1)
SW_PIN = 32   # Botón (Digital)

# Configuración del ADC para leer valores del joystick
vrx = ADC(Pin(VRX_PIN))
vry = ADC(Pin(VRY_PIN))
vrx.atten(ADC.ATTN_11DB)  # Configurar el rango de 0-3.3V
vry.atten(ADC.ATTN_11DB)

# Configuración del botón
sw = Pin(SW_PIN, Pin.IN, Pin.PULL_UP)

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

def publish_joystick_state(client, number):
    if client:
        try:
            client.publish(MQTT_TOPIC, str(number))
            print("📡 Número enviado:", number)
        except Exception as e:
            print("❌ Error al publicar:", e)

# Conectar Wi-Fi y MQTT
wlan = connect_wifi()
client = connect_mqtt() if wlan else None

if wlan and client:
    print("🎮 Esperando movimientos del joystick...")
    
    last_state = None  # Para evitar publicaciones repetidas
    
    while True:
        # Leer valores del joystick
        x_value = vrx.read()
        y_value = vry.read()
        button_pressed = not sw.value()  # Botón es activo en LOW

        # Determinar dirección según los valores de X e Y
        if x_value < 1000:
            number = 3  # LEFT
        elif x_value > 3000:
            number = 4  # RIGHT
        elif y_value < 1000:
            number = 1  # UP
        elif y_value > 3000:
            number = 2  # DOWN
        elif button_pressed:
            number = 5  # Botón presionado
        else:
            number = 0  # Centro

        # Enviar solo si hay un cambio de estado
        if number != last_state:
            publish_joystick_state(client, number)
            last_state = number

        time.sleep(0.2)  # Pequeña espera para evitar lecturas repetidas

else:
    print("❌ No se pudo conectar a Wi-Fi.")
