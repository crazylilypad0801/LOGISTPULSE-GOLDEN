import json
import os
import threading
import time

import paho.mqtt.client as mqtt

import repository

MQTT_HOST = os.getenv('MQTT_HOST', 'mosquitto')


def on_connect(client, userdata, flags, reason_code, properties=None):
    client.subscribe('logistpulse/store/+/device/+/telemetry')


def on_message(client, userdata, message):
    try:
        device = json.loads(message.payload.decode())
        device['topic'] = message.topic
        device['receivedAt'] = time.time()
        repository.store_telemetry(device)
    except Exception as error:
        print(f'mqtt telemetry error: {error}', flush=True)


def mqtt_loop():
    while True:
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        client.on_connect = on_connect
        client.on_message = on_message
        try:
            client.connect(MQTT_HOST, 1883, 60)
            client.loop_forever()
        except Exception as error:
            print(f'mqtt connection retrying: {error}', flush=True)
            time.sleep(2)


def start_mqtt_consumer():
    threading.Thread(target=mqtt_loop, daemon=True).start()