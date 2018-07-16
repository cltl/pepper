from socket import socket
from io import BytesIO
from PIL import Image

import numpy as np
import json


class InceptionClassifyClient:
    def __init__(self, address = ('localhost', 9999)):
        """
        Classify Images using Inception Model

        Parameters
        ----------
        address: (str, int)
            Address of Inception Model Host
        """
        self.address = address

    def classify(self, image):
        """
        Parameters
        ----------
        image: np.ndarray

        Returns
        -------
        classification: list of (float, list)
            List of confidence-object pairs, where object is a list of object synonyms
        """

        jpeg = self._convert_to_jpeg(image)
        jpeg_size = np.array([len(jpeg)], np.uint32)

        s = socket()
        s.connect(self.address)
        s.sendall(jpeg_size)
        s.sendall(jpeg)
        response = json.loads(s.recv(4096).decode())
        return response

    def _convert_to_jpeg(self, image):
        """
        Parameters
        ----------
        image: np.ndarray

        Returns
        -------
        encoded_image: bytes
        """

        with BytesIO() as jpeg_buffer:
            Image.fromarray(image).save(jpeg_buffer, format='JPEG')
            return jpeg_buffer.getvalue()



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