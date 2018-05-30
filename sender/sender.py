#!/usr/bin/env python
from flask import Flask
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

app = Flask(__name__)

port = int(os.getenv("PORT", 9099))

@app.route('/')
def hello_world():
    return "Hello!"

@app.route('/test')
def test_send():
    #Getting Service Info
    rmq_service = str(os.getenv('RMQ_SERVICE', 'p-rabbitmq'))
    service = json.loads(os.getenv('VCAP_SERVICES'))[rmq_service][0]
    amqp_url = service['credentials']['protocols']['amqp']['uri']

    #For Sending
    connection = pika.BlockingConnection(pika.URLParameters(amqp_url))
    channel = connection.channel()
    channel.exchange_declare(exchange='rabbitmq-demo', exchange_type='topic')
    channel.basic_publish(exchange='rabbitmq-demo',
                          routing_key='hello',
                          body='OK')
    connection.close()
    return "Sent!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port)