#!/usr/bin/env python
import json
import os
import pika
import logging
import sys

#For Logging
#log = logging.getLogger()
#log.setLevel(logging.DEBUG)
#ch = logging.StreamHandler(sys.stderr)
#ch.setLevel(logging.DEBUG)
#formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#ch.setFormatter(formatter)
#log.addHandler(ch)
def callback(ch, method, properties, body):
    print(" [x] Received %r" % body)

def main():
    #Getting Service Info
    rmq_service = str(os.getenv('RMQ_SERVICE', 'p-rabbitmq'))
    service = json.loads(os.getenv('VCAP_SERVICES'))[rmq_service][0]
    amqp_url = service['credentials']['protocols']['amqp']['uri']

    #For Receiving
    connection = pika.BlockingConnection(pika.URLParameters(amqp_url))
    channel = connection.channel()
    channel.exchange_declare(exchange='rabbitmq-demo', exchange_type='topic')
    result = channel.queue_declare(queue='hello',
                                   durable=True)
    queue_name = result.method.queue
    channel.queue_bind(exchange='rabbitmq-demo', queue=queue_name, routing_key='#')
    channel.basic_consume(callback, queue=queue_name)
    channel.start_consuming()

if __name__ == '__main__':
    main()