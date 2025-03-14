import time
import network
from machine import Pin, PWM
from umqtt.simple import MQTTClient

# Configuración
BUZZER_PIN = 16
MQTT_BROKER = "192.168.137.210"
MQTT_TOPIC_SUB = "kapm/control/buzzer"  # Tópico de suscripción
MQTT_CLIENT_ID = "ky012_buzzer_{}".format(int(time.time()))
WIFI_SSID = "KAREN 8870"
WIFI_PASSWORD = "e*905F06"

# Inicializar PWM para el buzzer
buzzer = PWM(Pin(BUZZER_PIN), freq=1000, duty=0)  # Comienza apagado

# Notas de la melodía (frecuencia en Hz y duración en ms)
MELODY = [
    (1000, 300), (1200, 300), (1400, 300), (1600, 300),
    (1800, 300), (2000, 300), (2200, 300), (2500, 300)
]

# Bandera para controlar la ejecución
buzzer_enabled = True

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
        client.set_callback(mqtt_callback)
        client.connect()
        client.subscribe(MQTT_TOPIC_SUB)
        print("✅ Conectado a MQTT y suscrito a:", MQTT_TOPIC_SUB)
        return client
    except Exception as e:
        print("❌ Error MQTT:", e)
        return None

def play_melody():
    """Reproduce la melodía y envía el estado al tópico MQTT."""
    global buzzer_enabled
    
    if buzzer_enabled:
        client.publish(MQTT_TOPIC_SUB, "1")  # 🔊 Buzzer encendido
        print("🔊 Reproduciendo melodía...")

        for note, duration in MELODY:
            buzzer.freq(note)  # Establecer frecuencia
            buzzer.duty(512)   # Activar sonido
            time.sleep(duration / 1000)  # Duración de la nota
            buzzer.duty(0)  # Silencio entre notas
            time.sleep(0.1)  # Pausa entre notas

        client.publish(MQTT_TOPIC_SUB, "0")  # 🔕 Buzzer apagado
        print("🔕 Melodía finalizada.")

def mqtt_callback(topic, msg):
    """Maneja los mensajes recibidos por MQTT."""
    global buzzer_enabled
    message = msg.decode("utf-8").strip().lower()
    
    if message == "on":
        buzzer_enabled = True
        print("🔊 Buzzer activado desde MQTT")
    elif message == "off":
        buzzer_enabled = False
        buzzer.duty(0)  # Apagar buzzer inmediatamente
        client.publish(MQTT_TOPIC_SUB, "0")  # Publicar apagado
        print("🔕 Buzzer desactivado desde MQTT")
    else:
        print("⚠️ Comando no reconocido:", message)

# Conectar Wi-Fi y MQTT
wlan = connect_wifi()
if wlan:
    client = connect_mqtt()
    
    while True:
        try:
            client.check_msg()  # Verificar mensajes MQTT
            
            if buzzer_enabled:
                play_melody()  # Reproducir melodía
            time.sleep(5)  # Esperar 5 segundos antes de la siguiente melodía
        
        except Exception as e:
            print("⚠️ Error en MQTT, intentando reconectar...", e)
            client = connect_mqtt()
else:
    print("❌ No se pudo conectar a Wi-Fi.")
