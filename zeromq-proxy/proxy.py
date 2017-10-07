"""ZeroMQ proxy in the middle to be able to inject events with custom data."""

from __future__ import print_function

import zmq
# import time
from multiprocessing import Process


EGYM_ZMQ_SERVER = "tcp://35.195.199.160:5556"
CUSTOM_ZMQ = "tcp://127.0.0.1:5556"


# def server(server):
#     """Server with custom events."""
#     context = zmq.Context()
#     socket = context.socket(zmq.REP)
#     socket.bind(server)
#     print("Running server {}".format(server))
#     # serves only 5 request and dies
#     while True:
#         # Wait for next request from client
#         message = socket.recv()
#         print("Server: Received request %s" % message)
#         socket.send("Server: Received %s" % server)
#         # time.sleep(1)


def client(origin_server, custom_server, topic_filter=""):
    """Client to stream data to our proxy."""
    context = zmq.Context()
    socket_origin = context.socket(zmq.SUB)
    socket_custom = context.socket(zmq.PUB)

    socket_origin.setsockopt(zmq.SUBSCRIBE, topic_filter)

    print("Connecting to origin server {}".format(origin_server))
    socket_origin.connect(origin_server)
    print("Connecting to custom server {}".format(custom_server))
    socket_custom.bind(custom_server)

    print("Ready to process messages")
    while True:
        message = socket_origin.recv()
        socket_custom.send(message)

        print("Proxied message: {}".format(message))


if __name__ == "__main__":
    # And pretened we have a custom ZMQ
    # Process(target=server, args=(CUSTOM_ZMQ,)).start()

    # Read all original data
    Process(target=client, args=(EGYM_ZMQ_SERVER, CUSTOM_ZMQ)).start()
