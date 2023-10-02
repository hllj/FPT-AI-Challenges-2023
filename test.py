import pika
import uuid
import os
import json

class RabbitMQ_Client(object):

    def __init__(self):
        url = os.environ.get('CLOUDAMQP_URL', 'amqp://ndtfovdr:pRLAJm2d7gIyFOaxlq74Q0PEg3fDsLnw@gerbil.rmq.cloudamqp.com/ndtfovdr')
        params = pika.URLParameters(url)
        params.socket_timeout = 10

        self.connection = pika.BlockingConnection(params) # Connect to CloudAMQP

        self.channel = self.connection.channel()

        result = self.channel.queue_declare(queue='', exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True)

        self.response = None
        self.corr_id = None

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            summary_info = body.decode("utf-8")
            self.response = summary_info

    def call(self, txt):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(
            exchange='',
            routing_key='request-queue',
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id,
            ),
            body=str(txt))
        self.connection.process_data_events(time_limit=None)
        self.connection.close()
        return str(self.response)

if __name__ == "__main__":
    txt = """
    Đây là một số thông tin mà tôi đã tổng hợp

    "Tuổi": 23 tuổi
    "Giới tính": Nam
    "Nhóm bệnh nhân": Người trưởng thành bình thường
    "Triệu chứng": Nuốt nước bọt thấy đau, sờ vào cổ thấy nóng nhẹ, có chút đờm
    "Khởi phát": 3 ngày trước
    "Bệnh đi kèm": Không
    "Thuốc hiện tại": Feburic
    "Dị ứng": Không
    """
    rabbitMQ = RabbitMQ_Client()

    print(" [x] Requesting")
    response = rabbitMQ.call(txt)
    print(f" [.] Got {response}")