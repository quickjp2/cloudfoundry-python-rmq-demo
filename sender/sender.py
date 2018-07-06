#!/usr/bin/env python
from flask import Flask, request
import flask
import json
import os
import pika
import uuid
import logging
import sys

#For Logging
LOGGER = logging.getLogger()
LOGGER.setLevel(logging.DEBUG)
#ch = logging.StreamHandler(sys.stderr)
#ch.setLevel(logging.DEBUG)
#formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#ch.setFormatter(formatter)
#log.addHandler(ch)

class RmqClient(object):
    """Class used to talk with RabbitMQ"""

    def __init__(self, amqp_url, exchange):
        """Class init"""
        self.response = None
        self.corr_id = None
        self.parameters = pika.URLParameters(amqp_url)
        self.exchange = exchange
        self.connection = None
        self.channel = None
        self.callback_queue = None

    def on_response(self, chan, method, props, body):
        """Function responsible for performing actions when receiving an incoming message
        Args:
            chan (pika.channel.Channel): The string used for hashing
            method (pika.spec.Basic.Deliver): Information about the received message
            props (pika.spec.BasicProperties): The properties of the received message
            body (dict): The body included in the received message
        """
        LOGGER.debug("Got a response...%r", body)
        if self.corr_id == props.correlation_id:
            self.response = body
        chan.basic_ack(delivery_tag=method.delivery_tag)

    def post_call(self, routing_key, msg, correlation_id=None):
        """Sends a message into rabbitmq without expecting a response back
        Args:
            routing_key (str): Message routing key
            msg (str): Message to send into the exchange
            correlation_id (int, optional): Optional id for message
        """
        LOGGER.debug("Let's send a post call")
        self.connection = pika.BlockingConnection(self.parameters)
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange=self.exchange, type='topic')
        self.channel.basic_publish(exchange=self.exchange,
                                   routing_key=routing_key,
                                   body=msg,
                                   properties=pika.BasicProperties(
                                       correlation_id=correlation_id,
                                       delivery_mode=2  # make message persistent
                                   ))
        self.connection.close()
        return " [x] Sent %r:%r" % (routing_key, msg), 202

    def rpc_call(self, routing_key, msg):
        """Sends a message and sets up a callback queue to listen for a response
        Args:
            routing_key (str): Message routing key
            msg (str): Message to send into the exchange
        """
        LOGGER.debug("Let's send a rpc call")
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.connection = pika.BlockingConnection(self.parameters)
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange=self.exchange, type='topic')
        result = self.channel.queue_declare(exclusive=True)
        self.callback_queue = result.method.queue
        self.channel.queue_bind(exchange=self.exchange, queue=self.callback_queue)
        self.channel.basic_consume(self.on_response, queue=self.callback_queue)
        LOGGER.debug("Sending message to rabbit")
        self.channel.basic_publish(exchange=self.exchange,
                                   routing_key=routing_key,
                                   properties=pika.BasicProperties(
                                       reply_to=self.callback_queue,
                                       correlation_id=self.corr_id,
                                   ),
                                   body=str(msg))
        LOGGER.debug("Message sent, waiting for response...")
        while self.response is None:
            self.connection.process_data_events()
        self.connection.close()
        return self.response

ROUTING_KEY = os.getenv('ROUTING_KEY', 'hello')
TEST_MESSAGE = os.getenv('TEST_MESSAGE', 'OK')
CONNECTION_COUNT = 0

CONNECTION = None

app = Flask(__name__)

port = int(os.getenv("PORT", 9099))

@app.route('/killSwitch')
def kill_switch():
    os._exit(0)

@app.route('/health')
def health():
    global CONNECTION_COUNT
    CONNECTION_COUNT += 1
    return 'Healthy', 200

@app.route('/')
def gui():
    # {"APP_NAME":""
    # "APP_INSTANCE":""
    # "APP_MEM":""
    # "APP_DISK":""
    # "APP_IP":""
    # "SERVICE_JSON":""}
    global CONNECTION_COUNT
    CONNECTION_COUNT += 1
    VCAP_APPLICATION = json.loads(os.getenv('VCAP_APPLICATION'))
    environment = os.environ
    environment['application_name'] = VCAP_APPLICATION['application_name']
    environment['application_id'] = VCAP_APPLICATION['application_id']
    environment['CONNECTION_COUNT'] = "{}".format(CONNECTION_COUNT)
    # environment['VCAP_APPLICATION'] = json.loads(environment['VCAP_APPLICATION'])
    return flask.render_template('gui.html', **environment)

@app.route('/test', methods=['GET', 'POST'])
def test_send():
    global CONNECTION_COUNT
    CONNECTION_COUNT += 1
    if request.method == 'POST':
        #For Sending
        payload = request.get_json()
        try:
            message = payload['message']
        except KeyError:
            return "Unable to find the message in your json :(\nI got {}".format(payload)
        RABBIT_CLIENT.post_call(ROUTING_KEY, message)
        # channel = CONNECTION.channel()
        # channel.exchange_declare(exchange=RMQ_EXCHANGE, exchange_type='topic')
        # channel.basic_publish(exchange=RMQ_EXCHANGE,
        #                     routing_key=ROUTING_KEY,
        #                     body=message)
        # CONNECTION.close()
        return "Sent! Message: {}".format(message)

    else:
        #For Sending
        RABBIT_CLIENT.post_call(ROUTING_KEY, TEST_MESSAGE)
        # channel = CONNECTION.channel()
        # channel.exchange_declare(exchange=RMQ_EXCHANGE, exchange_type='topic')
        # channel.basic_publish(exchange=RMQ_EXCHANGE,
        #                     routing_key=ROUTING_KEY,
        #                     body=TEST_MESSAGE)
        # CONNECTION.close()
        return "Sent! Message: {}\nIf you want to send a custom message, make a POST call with a json payload that contains the message key!".format(TEST_MESSAGE)

if __name__ == '__main__':
    #Getting Service Info
    rmq_service = str(os.getenv('RMQ_SERVICE', 'p-rabbitmq'))
    service = json.loads(os.getenv('VCAP_SERVICES'))[rmq_service][0]
    amqp_url = service['credentials']['protocols']['amqp']['uri']
    RABBIT_CLIENT = RmqClient(amqp_url, os.getenv('RMQ_EXCHANGE', 'rabbitmq-demo'))
    app.run(host='0.0.0.0', port=port)