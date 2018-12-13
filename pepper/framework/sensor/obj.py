from socket import socket, error as socket_error
from io import BytesIO
from PIL import Image

import numpy as np
import json


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
    def center(self):
        """
        Returns
        -------
        center: tuple
        """
        return (self.x0 + self.width / 2, self.y0 + self.height / 2)

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

    def overlap(self, other):
        """
        Calculate Overlap Factor

        Parameters
        ----------
        other: Bounds

        Returns
        -------
        overlap: float
        """

        intersection = self.intersection(other)

        return min(intersection.area / self.area, self.area / intersection.area)

    def is_subset_of(self, other):
        """
        Parameters
        ----------
        other: Bounds

        Returns
        -------
        is_subset_of: bool
            Whether 'other' Bounds is subset of 'this' Bounds
        """
        return self.x0 >= other.x0 and self.y0 >= other.y0 and self.x1 <= other.x1 and self.y1 <= other.y1

    def is_superset_of(self, other):
        """
        Parameters
        ----------
        other: Bounds

        Returns
        -------
        is_superset_of: bool
            Whether 'other' Bounds is superset of 'this' Bounds
        """
        return self.x0 <= other.x0 and self.y0 <= other.y0 and self.x1 >= other.x1 and self.y1 >= other.y1

    def equals(self, other):
        """
        Parameters
        ----------
        other: Bounds

        Returns
        -------
        equals: bool
         Whether 'other' bounds equals 'this' bounds
        """
        return self.x0 == other.x0 and self.y0 == other.y0 and self.x1 == other.x1 and self.y1 == other.y1

    def scaled(self, x_scale, y_scale):
        """
        Return Scaled Bounds Object

        Parameters
        ----------
        x_scale: float
        y_scale: float

        Returns
        -------
        bounds: Bounds
            Scaled Bounds object
        """
        return Bounds(self.x0 * x_scale, self.y0 * y_scale, self.x1 * x_scale, self.y1 * y_scale)

    def __repr__(self):
        return "Bounds[({:3f}, {:3f}), ({:3f}, {:3f})]".format(self.x0, self.y0, self.x1, self.y1)


class CocoObject(object):
    def __init__(self, id, name, bounds, confidence):
        """
        CoCo Object Information

        Parameters
        ----------
        id: int
            Unique id for object of name 'name'
        name: str
            Name of object
        bounds: Bounds
            Bounding Box of object in frame [0..1]
        confidence: float
            Confidence of Object Classification [0..1]
        """
        self._id = id
        self._name = name
        self._bounds = bounds
        self._confidence = confidence

    @property
    def id(self):
        """
        Returns
        -------
        id: int
            Unique id for object of name 'name'
        """
        return self._id

    @property
    def name(self):
        """
        Returns
        -------
        name: str
            Name of object
        """
        return self._name

    @property
    def bounds(self):
        """
        Returns
        -------
        bounds: Bounds
            Bounding Box of object in frame [0..1]
        """
        return self._bounds

    @property
    def confidence(self):
        """
        Returns
        -------
        confidence: float
            Confidence of Object Classification [0..1]
        """
        return self._confidence


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
            Image.fromarray(image).save_person(jpeg_buffer, format='JPEG')
            return jpeg_buffer.getvalue()


class CocoClassifyClient:

    CLASSES = 90
    PORT = 35621

    def __init__(self, address=('localhost', PORT)):
        """
        CoCo Service Interface

        Parameters
        ----------
        address
        """
        self.address = address

    def classify(self, image):
        """
        Parameters
        ----------
        image: np.ndarray
            RGB image to classify

        Returns
        -------
        objects: list of CocoObject
            Object classifications made from image
        """

        try:

            # Connect to CoCo Service
            s = socket()
            s.connect(self.address)

            # Send Image to CoCo Service
            s.sendall(np.array(image.shape, np.uint32))
            s.sendall(image)

            # Receive Image Classification from Service
            response_length = np.frombuffer(s.recv(4), np.uint32)[0]
            classes, scores, boxes = json.loads(self._recv_all(s, response_length).decode())

            # Wrap information into CocoObject instances
            objects = []
            for cls, confidence, box in zip(classes, scores, boxes):
                objects.append(CocoObject(cls["id"], cls["name"], Bounds(box[1], box[0], box[3], box[2]), confidence))
            return objects

        except socket_error as e:
            raise RuntimeError(
                "Can't connect to Coco Service at {}. Are you sure the service is running?".format(self.address))

    def _recv_all(self, sock, n):
        """
        Receive exactly n bytes from socket connection

        Parameters
        ----------
        sock: socket
        n: int

        Returns
        -------
        bytes: bytearray
        """

        buffer = bytearray()
        while len(buffer) < n:
            buffer.extend(sock.recv(4096))
        return buffer