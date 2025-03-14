import time
import network
from machine import Pin, PWM
from umqtt.simple import MQTTClient

# Configuración
BUZZER_PIN = 16
MQTT_BROKER = "192.168.137.210"
MQTT_TOPIC_SUB = "kapm/buzzer/pasivo"
MQTT_CLIENT_ID = "ky012_buzzer_{}".format(int(time.time()))
WIFI_SSID = "KAREN 8870"
WIFI_PASSWORD = "e*905F06"

# Inicializar PWM para el buzzer pasivo
buzzer = PWM(Pin(BUZZER_PIN), duty=0)  # Comienza apagado

# Nueva melodía para buzzer pasivo (frecuencia en Hz, duración en ms)
MELODY = [
    (523, 200), (587, 200), (659, 200), (698, 200),  # Do, Re, Mi, Fa
    (784, 300), (880, 300), (988, 300), (1047, 500),  # Sol, La, Si, Do
    (988, 200), (880, 200), (784, 200), (698, 200)  # Inversión descendente
]

# Estado del buzzer
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
    """Reproduce la melodía en un buzzer pasivo y envía estado MQTT."""
    global buzzer_enabled
    
    if buzzer_enabled:
        client.publish(MQTT_TOPIC_SUB, "1")  # 🔊 Enviar estado ON
        print("🔊 Reproduciendo melodía en buzzer pasivo...")

        for note, duration in MELODY:
            buzzer.freq(note)  # Ajustar frecuencia de la nota
            buzzer.duty(512)   # Activar sonido
            time.sleep_ms(duration)  # Mantener nota
            buzzer.duty(0)  # Silencio entre notas
            time.sleep_ms(100)  # Pausa

        client.publish(MQTT_TOPIC_SUB, "0")  # 🔕 Enviar estado OFF
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
        print( message)

# Conectar Wi-Fi y MQTT
wlan = connect_wifi()
if wlan:
    client = connect_mqtt()
    
    while True:
        try:
            client.check_msg()  # Verificar mensajes MQTT
            
            if buzzer_enabled:
                play_melody()  # Reproducir melodía
            time.sleep(5)  # Esperar 5 segundos antes de repetir
        
        except Exception as e:
            print("⚠️ Error en MQTT, intentando reconectar...", e)
            client = connect_mqtt()
else:
    print("❌ No se pudo conectar a Wi-Fi.")
