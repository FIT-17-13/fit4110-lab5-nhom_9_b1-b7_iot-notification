from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pika
import os
import json

app = FastAPI(title="Notification API - Team 9")

# Schema payload gửi thông báo
class NotificationPayload(BaseModel):
    recipient: str
    title: str
    message: str
    channel: str # Ví dụ: telegram, sms, email

    class Config:
        json_schema_extra = {
            "example": {
                "recipient": "customer_01",
                "title": "Cập nhật Kén Delivery",
                "message": "Kiện hàng thực phẩm #402 đã đến trạm trung chuyển.",
                "channel": "telegram"
            }
        }

def get_mq_channel():
    # Kết nối tới RabbitMQ thông qua biến môi trường
    url = os.getenv("RABBITMQ_URL", "amqp://notify_admin:secret_mq_password@rabbitmq:5672/")
    parameters = pika.URLParameters(url)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    
    # Khai báo hàng đợi (durable=True để không mất tin nhắn khi RabbitMQ restart)
    channel.queue_declare(queue='notification_queue', durable=True)
    return connection, channel

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "notification-api"}

@app.post("/api/v1/notify")
def send_notification(payload: NotificationPayload):
    try:
        connection, channel = get_mq_channel()
        channel.basic_publish(
            exchange='',
            routing_key='notification_queue',
            body=json.dumps(payload.model_dump()),
            properties=pika.BasicProperties(
                delivery_mode=2, # Đánh dấu tin nhắn là persistent (lưu vào ổ cứng)
            ))
        connection.close()
        return {"status": "success", "detail": "Message queued via RabbitMQ"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MQ Error: {str(e)}")
    