from socket import socket, error as socket_error
from io import BytesIO
from PIL import Image

import numpy as np
import json

import logging


class Bounds(object):
    def __init__(self, x0, y0, x1, y1):
        """
        Parameters
        ----------
        x0: float
        y0: float
        x1: float
        y1: float
        """

        if x0 >= x1 or y0 >= y1:
            raise ValueError("Rectangle Error: Point (x1,y1) must be bigger than point (x0, y0)")

        self._x0 = x0
        self._y0 = y0
        self._x1 = x1
        self._y1 = y1

    @property
    def x0(self):
        """
        Returns
        -------
        x0: float
        """
        return self._x0

    @property
    def y0(self):
        """
        Returns
        -------
        y0: float
        """
        return self._y0

    @property
    def x1(self):
        """
        Returns
        -------
        x1: float
        """
        return self._x1

    @property
    def y1(self):
        """
        Returns
        -------
        y1: float
        """
        return self._y1

    @property
    def width(self):
        """
        Returns
        -------
        width: float
        """
        return self.x1 - self.x0

    @property
    def height(self):
        """
        Returns
        -------
        height: float
        """
        return self.y1 - self.y0

    @property
    def area(self):
        """
        Returns
        -------
        area: float
        """
        return self.width * self.height

    def intersection(self, bounds):
        """
        Parameters
        ----------
        bounds: Bounds

        Returns
        -------
        intersection: Bounds or None
        """

        x0 = max(self.x0, bounds.x0)
        y0 = max(self.y0, bounds.y0)
        x1 = min(self.x1, bounds.x1)
        y1 = min(self.y1, bounds.y1)

        return None if x0 >= x1 or y0 >= y1 else Bounds(x0, y0, x1, y1)

    def overlap(self, bounds):
        """
        Calculate Overlap Factor

        Parameters
        ----------
        bounds: Bounds

        Returns
        -------
        overlap: float
        """
        return min(self.intersection(bounds).area / self.area, 1)


class InceptionClassifyClient:
    def __init__(self, address=('localhost', 9999)):
        """
        Classify Images using Inception Model

        Parameters
        ----------
        address: (str, int)
            Address of Inception Model Host
        """
        self.address = address
        self._log = logging.getLogger(self.__class__.__name__)

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

        try:
            s = socket()
            s.connect(self.address)
            s.sendall(jpeg_size)
            s.sendall(jpeg)
            response = json.loads(s.recv(4096).decode())
            return response
        except socket_error as e:
            raise RuntimeError(
                "Can't connect to Inception Service at {}. Are you sure the service is running?".format(self.address))


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

    CLASSES = 90
    PORT = 35621

    def __init__(self, address=('localhost', PORT)):
        self.address = address
        self._log = logging.getLogger(self.__class__.__name__)

    def classify(self, image):
        try:
            s = socket()
            s.connect(self.address)

            s.sendall(np.array(image.shape, np.uint32))
            s.sendall(image)

            response_length = np.frombuffer(s.recv(4), np.uint32)[0]
            response = json.loads(self._recv_all(s, response_length).decode())

            return response
        except socket_error as e:
            raise RuntimeError(
                "Can't connect to Coco Service at {}. Are you sure the service is running?".format(self.address))

    def _recv_all(self, sock, n):
        buffer = bytearray()
        while len(buffer) < n:
            buffer.extend(sock.recv(4096))
        return buffer