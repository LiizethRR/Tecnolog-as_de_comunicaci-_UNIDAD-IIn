from machine import Pin
import time
import network
from umqtt.simple import MQTTClient

# Configuración de los pines
clk = Pin(14, Pin.IN, Pin.PULL_UP)  # Pin para CLK (Clock)
dt = Pin(12, Pin.IN, Pin.PULL_UP)   # Pin para DT (Data)
sw = Pin(13, Pin.IN, Pin.PULL_UP)   # Pin para el botón (SW)

# Configuración de MQTT y Wi-Fi
MQTT_BROKER = "192.168.137.210"
MQTT_TOPIC = "kapm/sensor/encoder"
MQTT_CLIENT_ID = "encoder_sensor_{}".format(int(time.time()))
WIFI_SSID = "KAREN 8870"
WIFI_PASSWORD = "e*905F06"

# Variables globales para manejar la rotación
last_clk_state = clk.value()
counter = 0
client = None  # Cliente MQTT

# Conexión Wi-Fi
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

# Conexión MQTT
def connect_mqtt():
    global client
    try:
        client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER)
        client.connect()
        print("✅ Conectado a MQTT")
    except Exception as e:
        print("❌ Error MQTT:", e)
        client = None

# Función para manejar la rotación
def rotar_encoder(pin):
    global last_clk_state, counter, client
    clk_state = clk.value()
    dt_state = dt.value()

    if clk_state != last_clk_state:
        if dt_state != clk_state:
            counter += 1  # Rotación en una dirección
        else:
            counter -= 1  # Rotación en la otra dirección
        
        print("Contador:", counter)  # Imprime el valor del contador
        
        # Enviar datos a MQTT
        if client:
            try:
                client.publish(MQTT_TOPIC, str(counter))
                print(f"📡 Datos enviados: {counter}")
            except Exception as e:
                print("❌ Error al publicar:", e)
                connect_mqtt()  # Intentar reconectar MQTT

    last_clk_state = clk_state  # Actualizar el estado de CLK

# Detectar pulsación del botón
def verificar_boton(pin):
    if not sw.value():
        print("🟢 Botón presionado")

# Conectar Wi-Fi y MQTT
wlan = connect_wifi()
if wlan:
    connect_mqtt()

# Configurar interrupciones
clk.irq(trigger=Pin.IRQ_RISING, handler=rotar_encoder)  
sw.irq(trigger=Pin.IRQ_FALLING, handler=verificar_boton)

# Mantener el programa corriendo
while True:
    if not wlan.isconnected():
        print("⚠️ Wi-Fi desconectado, reconectando...")
        wlan = connect_wifi()

    if client is None:
        print("⚠️ Reintentando conexión MQTT...")
        connect_mqtt()
    
    time.sleep(1)  # Mantener activo
