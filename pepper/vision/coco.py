import numpy as np
from socket import socket
import json


class CocoClassifyClient:

    PORT = 35621

    def __init__(self, address = ('localhost', PORT)):
        self.address = address

    def classify(self, image):
        sock = socket()
        sock.connect(self.address)

        sock.sendall(np.array(image.shape, np.uint32))
        sock.sendall(image)

        response_length = np.frombuffer(sock.recv(4), np.uint32)[0]
        response = json.loads(self._recv_all(sock, response_length).decode())

        return response

    def _recv_all(self, sock, n):
        buffer = bytearray()
        while len(buffer) < n:
            buffer.extend(sock.recv(4096))
        return buffer