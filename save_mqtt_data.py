import paho.mqtt.client as mqtt
import time
from influxdb_client import InfluxDBClient, Point, WritePrecision
import json
import base64

import os
from dotenv import load_dotenv
load_dotenv()


# MQTT
broker = os.getenv("MQTT_BROKER")
port = int(os.getenv("MQTT_PORT"))
topic = os.getenv("MQTT_TOPIC")

# InfluxDB
influxdb_url = os.getenv("INFLUXDB_URL")
influxdb_token = os.getenv("INFLUXDB_TOKEN")
influxdb_org = os.getenv("INFLUXDB_ORG")
influxdb_bucket = os.getenv("INFLUXDB_BUCKET")


# Crear un cliente de InfluxDB
influxdb_client = InfluxDBClient(url=influxdb_url, token=influxdb_token)
write_api = influxdb_client.write_api()

# Variable para verificar conexión
connected = False

# Callback cuando el cliente se conecta al broker
def on_connect(client, userdata, flags, rc):
    global connected
    if rc == 0:
        print("Conexión exitosa")
        client.subscribe(topic)
        print(f"Suscrito al tema '{topic}'")
        connected = True
    else:
        print(f"Error de conexión. Código: {rc}")

# Callback cuando recibe un mensaje
def on_message(client, userdata, message):
    payload = message.payload.decode()  # Decodificar el mensaje
    print(f"Mensaje recibido en '{message.topic}': {payload}")
    
    # Guardar el mensaje en InfluxDB
    try:    
        msg = json.loads(payload)
        rx = msg["rxInfo"][0]
        raw_data = base64.b64decode(msg["data"])
        hex_data = raw_data.hex()
        point = (
            Point("romosa")
            .tag("devEui", msg["deviceInfo"]["devEui"])
            .field("fcnt", int(msg["fCnt"]))
            .field("rssi", int(rx["rssi"]))
            .field("snr", float(rx["snr"]))
            .field("data", int(hex_data[:4], 16))
            .field("state", int(hex_data[-2:], 16))
        )

        write_api.write(bucket=influxdb_bucket, org=influxdb_org, record=point)
        print("Datos guardados en InfluxDB")
    except Exception as e:
        print(f"Error al guardar en InfluxDB: {e}")

# Callback cuando el cliente se desconecta del broker
def on_disconnect(client, userdata, rc):
    global connected
    print(f"Desconectado. Código: {rc}")
    connected = False

# Crear una instancia del cliente MQTT
mqtt_client = mqtt.Client()

# Asignar las funciones de callback
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.on_disconnect = on_disconnect

# Conectar al broker MQTT
try:
    mqtt_client.reconnect_delay_set(min_delay=1, max_delay=60)

    mqtt_client.connect(broker, port, 60)
    mqtt_client.loop_start()  # Inicia el bucle de red para manejar mensajes

    # Mantener el cliente conectado y en espera de mensajes
    while True:
        time.sleep(1)  # Mantener el bucle principal activo
except KeyboardInterrupt:
    print("Interrumpido por el usuario. Desconectando...")
finally:
    mqtt_client.loop_stop()
    mqtt_client.disconnect()
    influxdb_client.close()  # Cerrar la conexión a InfluxDB
    print("Cliente desconectado")


'''
{
  "deduplicationId": "1322464f-67bd-4968-8635-6366abe2b650",
  "time": "2025-12-25T21:43:03.621+00:00",
  "deviceInfo": {
    "tenantId": "af4f7c49-a59c-4143-97f1-50b9152dfc0a",
    "tenantName": "ChirpStack",
    "applicationId": "24d6e444-25d8-48a6-8f0e-78fad4c2d374",
    "applicationName": "Romosa",
    "deviceProfileId": "0e1ca62a-b802-44ee-9772-60b951303a75",
    "deviceProfileName": "Romosa_AU915_01",
    "deviceName": "machine_015",
    "devEui": "ffff00000000000f",
    "deviceClassEnabled": "CLASS_A",
    "tags": {}
  },
  "devAddr": "0058414c",
  "adr": false,
  "dr": 3,
  "fCnt": 97208,
  "fPort": 2,
  "confirmed": false,
  "data": "AAAD",
  "rxInfo": [
    {
      "gatewayId": "24e124fffffafb1b",
      "uplinkId": 396,
      "gwTime": "2025-12-25T21:43:03.621617+00:00",
      "nsTime": "2025-12-25T21:43:10.325209838+00:00",
      "timeSinceGpsEpoch": "1450734201.621s",
      "rssi": -77,
      "snr": 11.5,
      "location": {},
      "context": "y+wFUw==",
      "crcStatus": "CRC_OK"
    }
  ],
  "txInfo": {
    "frequency": 916800000,
    "modulation": {
      "lora": {
        "bandwidth": 125000,
        "spreadingFactor": 9,
        "codeRate": "CR_4_5"
      }
    }
  },
  "regionConfigId": "au915_1"
}
'''