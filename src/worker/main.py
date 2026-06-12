import pika
from pika.exceptions import AMQPConnectionError
import os
import json
import time

def process_notification(ch, method, properties, body):
    data = json.loads(body)
    
    print(f"[WORKER] Đang chuẩn bị gửi qua kênh: {data.get('channel', 'unknown').upper()}")
    print(f"[WORKER] Người nhận: {data.get('recipient')}")
    print(f"[WORKER] Tiêu đề: {data.get('title')}")
    print(f"[WORKER] Nội dung: {data.get('message')}")
    
    time.sleep(1.5) 
    
    print(f"[WORKER] Gửi thành công!\n" + "-"*40)
    ch.basic_ack(delivery_tag=method.delivery_tag)

def main():
    url = os.getenv("RABBITMQ_URL", "amqp://notify_admin:secret_mq_password@rabbitmq:5672/")
    
    connection = None
    channel = None
    connected = False
    
    while not connected:
        try:
            parameters = pika.URLParameters(url)
            connection = pika.BlockingConnection(parameters)
            channel = connection.channel()
            channel.queue_declare(queue='notification_queue', durable=True)
            connected = True
        except AMQPConnectionError:
            print("[WORKER] RabbitMQ chưa sẵn sàng, đang thử lại...")
            time.sleep(2)

    # Khẳng định với Pylance rằng channel đã được khởi tạo thành công
    assert channel is not None

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='notification_queue', on_message_callback=process_notification)
    
    print("[WORKER] Dịch vụ đã sẵn sàng. Đang chờ thông báo mới...")
    channel.start_consuming()

if __name__ == '__main__':
    main()