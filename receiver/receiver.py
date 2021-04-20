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

def send_response(chan, props, body):
    """Function to finish the reply back to rabbitmq
    Args:
        chan (pika.channel.Channel): The string used for hashing
        props (pika.spec.BasicProperties): The properties of the received message
        body (dict): The body included in the received message
        reply_to_props (pika.spec.BasicProperties): The properties of the response message
        response (dict, optional): The response from the service
    """
    exchange = os.getenv('RMQ_EXCHANGE')
    try:
        chan.basic_publish(exchange=exchange,
                           routing_key=props.reply_to,
                           properties=pika.BasicProperties(correlation_id=props.correlation_id, delivery_mode=1),
                           body=json.dumps(body))
    except:
        # print("No reply_to is specified, no reply needed")
        print("Unexpected error: %r", sys.exc_info()[0])
        response = "{0}".format(sys.exc_info()[0]), 500

def callback(ch, method, properties, raw_body):
    print(" [x] Received %r" % raw_body)
    try:
        if isinstance(raw_body, str):
            body = json.loads(raw_body)
        else:
            converted_input = str(raw_body, 'utf-8')
            print(" Input converted to %r" % converted_input)
            try:
                body = json.loads(converted_input)
            except json.decoder.JSONDecodeError:
                print("Input is just a string")
                body = {"message": converted_input}
    except:
        print("Some unknown error")
    else:
        print("Let's do something with the input!")
        if 'sleep' in body:
            sleep(body['sleep'])
        print("I'M GONNA PRINT IT!\n {}".format(body))
    finally:
        try:
            send_response(ch, properties, body)
        except:
            print("Something went wrong")
        finally:
            ch.basic_ack(delivery_tag=method.delivery_tag)

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
    channel.queue_bind(exchange=os.getenv('RMQ_EXCHANGE'), queue=queue_name, routing_key=os.getenv('BINDING_KEY','#'))
    channel.basic_consume(on_message_callback=callback, queue=queue_name)
    channel.start_consuming()

if __name__ == '__main__':
    main()