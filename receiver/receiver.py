#!/usr/bin/env python
import json
import os
import pika
import logging
import sys
from time import sleep

#For Logging
#log = logging.getLogger()
#log.setLevel(logging.DEBUG)
#ch = logging.StreamHandler(sys.stderr)
#ch.setLevel(logging.DEBUG)
#formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#ch.setFormatter(formatter)
#log.addHandler(ch)

RMQ_EXCHANGE = os.getenv('RMQ_EXCHANGE', 'rabbitmq-demo')
BINDING_KEY = os.getenv('BINDING_KEY', '#')

def callback(ch, method, properties, raw_body):
    print(" [x] Received %r" % raw_body)
    # if isinstance(raw_body, str):
    #     body = json.loads(raw_body)
    # else:
    #     body = json.loads(str(raw_body, 'utf-8'))
    # if 'sleep' in raw_body:
    #     sleep(10)

def main():
    #Getting Service Info
    rmq_service = str(os.getenv('RMQ_SERVICE', 'p-rabbitmq'))
    service = json.loads(os.getenv('VCAP_SERVICES'))[rmq_service][0]
    amqp_url = service['credentials']['protocols']['amqp']['uri']

    #For Receiving
    connection = pika.BlockingConnection(pika.URLParameters(amqp_url))
    channel = connection.channel()
    channel.exchange_declare(exchange=os.getenv('RMQ_EXCHANGE', 'rabbitmq-demo'), exchange_type='topic')
    result = channel.queue_declare(queue='hello', durable=True)
    queue_name = result.method.queue
    channel.queue_bind(exchange='rabbitmq-demo', queue=queue_name, routing_key=os.getenv('BINDING_KEY','#'))
    channel.basic_consume(callback, queue=queue_name)
    channel.start_consuming()

if __name__ == '__main__':
    main()