"""ZeroMQ proxy in the middle to be able to inject events with custom data."""

from __future__ import print_function

import zmq
# import time
from multiprocessing import Process, Queue


EGYM_ZMQ_SERVER = "tcp://35.195.199.160:5556"
CUSTOM_ZMQ = "tcp://127.0.0.1:5556"
ANDROID_ZMQ = "tcp://*:5557"


def server(android_server, publisher_queue):
    """Server with custom events."""
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind(android_server)
    print("Running Android ZMQ server {}".format(android_server))

    while True:
        # Wait for next request from client
        message = socket.recv()
        publisher_queue.put(message)

        socket.send('pong')
        print("Android Server: [%s]" % message)


def publisher(custom_server, publisher_queue):
    """A publisher jo join all the streams."""
    context = zmq.Context()
    socket_custom = context.socket(zmq.PUB)

    socket_custom.bind(custom_server)

    while True:
        message = publisher_queue.get()
        socket_custom.send(message)


def egym_client(origin_server, socket_custom, topic_filter=""):
    """Client to stream data to our proxy."""
    context = zmq.Context()
    socket_origin = context.socket(zmq.SUB)
    socket_origin.setsockopt(zmq.SUBSCRIBE, topic_filter)

    print("Connecting to origin server {}".format(origin_server))
    socket_origin.connect(origin_server)

    print("Ready to process messages")
    while True:
        message = socket_origin.recv()
        publisher_queue.put(message)

        print("Proxied message: {}".format(message))


if __name__ == "__main__":
    publisher_queue = Queue()

    # Create a publisher process to let clients to subscribe
    Process(target=publisher, args=(CUSTOM_ZMQ, publisher_queue)).start()

    # Forward all original eGYM data to a custom ZMQ
    Process(target=egym_client, args=(EGYM_ZMQ_SERVER, publisher_queue)).start()

    # And pretend we have a custom ZMQ server for wearables
    Process(target=server, args=(ANDROID_ZMQ, publisher_queue)).start()
