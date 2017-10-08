"""ZeroMQ proxy in the middle to be able to inject events with custom data."""

from __future__ import print_function

import zmq
# import time
from multiprocessing import Process


EGYM_ZMQ_SERVER = "tcp://35.195.199.160:5556"
CUSTOM_ZMQ = "tcp://127.0.0.1:5556"
ANDROID_ZMQ = "tcp://*:5557"


def server(android_server, custom_server):
    """Server with custom events."""
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind(android_server)
    print("Running Android ZMQ server {}".format(android_server))

    socket_custom = get_publisher(custom_server)
    while True:
        # Wait for next request from client
        message = socket.recv()
        socket.send('pong')
        print("Android Server: Received request %s" % message)
        socket_custom.send(message)


def get_publisher(server):
    """Get a custom piublisher."""
    context = zmq.Context()
    socket_custom = context.socket(zmq.PUB)

    socket_custom.bind(server)

    return socket_custom


def egym_client(origin_server, custom_server, topic_filter=""):
    """Client to stream data to our proxy."""
    context = zmq.Context()
    socket_origin = context.socket(zmq.SUB)
    socket_origin.setsockopt(zmq.SUBSCRIBE, topic_filter)

    print("Connecting to origin server {}".format(origin_server))
    socket_origin.connect(origin_server)

    socket_custom = get_publisher(custom_server)

    print("Ready to process messages")
    while True:
        message = socket_origin.recv()
        socket_custom.send(message)

        print("Proxied message: {}".format(message))


if __name__ == "__main__":
    # And pretened we have a custom ZMQ server for wearables
    Process(target=server, args=(ANDROID_ZMQ, CUSTOM_ZMQ)).start()

    # forward all original eGYM data to a custom ZMQ
    # Process(target=egym_client, args=(EGYM_ZMQ_SERVER, CUSTOM_ZMQ)).start()
