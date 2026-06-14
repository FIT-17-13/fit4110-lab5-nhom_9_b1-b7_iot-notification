import ssl
import json
import pandas as pd
import os
from paho.mqtt import client as mqtt

# Load Registry
df_registry = pd.read_csv('IoT_device_registry.csv')
device_map = df_registry.set_index('device_id').to_dict('index')

def classify_data(data):
    # Kiểm tra lỗi cảm biến
    if data.get('temperature_c') is None or data.get('humidity_percent') is None:
        return "sensor_error", "medium", "missing_sensor_value"
    
    # Kiểm tra ngưỡng Danger
    if data['temperature_c'] >= 40 or data['co2_ppm'] >= 1800 or data['smoke_ppm'] >= 1.0:
        return "danger", "high", "critical_threshold_exceeded"
    
    # Kiểm tra ngưỡng Warning
    if data['temperature_c'] >= 35 or data['humidity_percent'] >= 85 or data['battery_percent'] < 20:
        return "warning", "medium", "threshold_warning"
        
    return "normal", "none", "environment_normal"

def on_message(client, userdata, msg):
    try:
        raw_payload = json.loads(msg.payload.decode())
        
        # Validate Schema
        required = ['event_id', 'timestamp', 'device_id', 'temperature_c', 'humidity_percent', 'motion_detected']
        if not all(k in raw_payload for k in required):
            print("[ERROR] Thiếu trường bắt buộc")
            return

        # Enrich & Classify
        device_id = raw_payload.get('device_id')
        if device_id not in device_map:
            status, alert, reason = "invalid_device", "high", "device_not_registered"
            location = "Unknown Area"
        else:
            status, alert, reason = classify_data(raw_payload)
            location = device_map[device_id]['location']

        # Transform
        processed_event = {
            "event_id": f"sensor-event-{raw_payload['event_id']}",
            "event_type": "sensor.reading.processed",
            "source_service": "team-iot",
            "timestamp": raw_payload['timestamp'],
            "raw_event_id": raw_payload['event_id'],
            "device_id": device_id,
            "location": location,
            "temperature_c": raw_payload.get('temperature_c'),
            "humidity_percent": raw_payload.get('humidity_percent'),
            "motion_detected": raw_payload.get('motion_detected'),
            "status": status,
            "alert_level": alert,
            "reason": reason
        }

        client.publish("smart-campus/events/sensor", json.dumps(processed_event))
        print(f"[IOT] Đã xử lý: {device_id} - {status}")

    except Exception as e:
        print(f"[ERROR] Lỗi hệ thống: {e}")

# Kết nối HiveMQ
client = mqtt.Client(protocol=mqtt.MQTTv5)
client.username_pw_set("DVKN_IOT_2026", "ThaiBao12A@")
client.tls_set(tls_version=ssl.PROTOCOL_TLS_CLIENT)
client.on_message = on_message

client.connect("f6f78e87db4a4c189dd3d706745a5e93.s1.eu.hivemq.cloud", 8883)
client.subscribe("smart-campus/raw/iot/environment", qos=1)

print("Service IoT Ingestion đã sẵn sàng...")
client.loop_forever()