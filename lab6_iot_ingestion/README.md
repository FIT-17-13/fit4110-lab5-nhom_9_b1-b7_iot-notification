# IoT Ingestion Service - Documentation

## 1. Mục tiêu
Service nhận dữ liệu từ cảm biến IoT (MQTT), thực hiện lọc, làm sạch và làm giàu dữ liệu trước khi gửi đi.

## 2. Thông tin tích hợp
- **Topic đầu vào:** `smart-campus/raw/iot/environment`
- **Topic đầu ra:** `smart-campus/events/sensor` (JSON)
- **Endpoint kiểm tra:** `GET /health` (Nếu có)

## 3. Schema dữ liệu đầu ra (Đã chuẩn hóa)
Các nhóm khác vui lòng subscribe topic `smart-campus/events/sensor` để nhận dữ liệu theo schema sau:
```json
{
  "event_id": "sensor-event-001",
  "status": "normal",
  "alert_level": "none",
  "device_id": "esp32-lab-a101",
  "temperature_c": 31.2,
  "reason": "environment_normal"
}