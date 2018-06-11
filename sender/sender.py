#!/usr/bin/env python
from flask import Flask, request
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

RMQ_EXCHANGE = os.getenv('RMQ_EXCHANGE', 'rabbitmq-demo')
ROUTING_KEY = os.getenv('ROUTING_KEY', 'hello')
TEST_MESSAGE = os.getenv('TEST_MESSAGE', 'OK')

CONNECTION = None

app = Flask(__name__)

port = int(os.getenv("PORT", 9099))

@app.route('/')
def hello_world():
    return "Hello!"

@app.route('/test', methods=['GET', 'POST'])
def test_send():
    if request.method == 'POST':
        #For Sending
        payload = request.get_json()
        try:
            message = payload['message']
        except KeyError:
            return "Unable to find the message in your json :(\nI got {}".format(payload)
        channel = CONNECTION.channel()
        channel.exchange_declare(exchange=RMQ_EXCHANGE, exchange_type='topic')
        channel.basic_publish(exchange=RMQ_EXCHANGE,
                            routing_key=ROUTING_KEY,
                            body=message)
        CONNECTION.close()
        return "Sent! Message: {}".format(message)

    else:
        #For Sending
        channel = CONNECTION.channel()
        channel.exchange_declare(exchange=RMQ_EXCHANGE, exchange_type='topic')
        channel.basic_publish(exchange=RMQ_EXCHANGE,
                            routing_key=ROUTING_KEY,
                            body=TEST_MESSAGE)
        CONNECTION.close()
        return "Sent! Message: {}\nIf you want to send a custom message, make a POST call with a json payload that contains the message key!".format(TEST_MESSAGE)

if __name__ == '__main__':
    #Getting Service Info
    rmq_service = str(os.getenv('RMQ_SERVICE', 'p-rabbitmq'))
    service = json.loads(os.getenv('VCAP_SERVICES'))[rmq_service][0]
    amqp_url = service['credentials']['protocols']['amqp']['uri']
    CONNECTION = pika.BlockingConnection(pika.URLParameters(amqp_url))
    app.run(host='0.0.0.0', port=port)