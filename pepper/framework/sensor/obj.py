from pepper.framework.abstract import AbstractImage
from pepper import ObjectDetectionTarget

import numpy as np

from socket import socket, error as socket_error
import json

from typing import List


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

        if x0 > x1 or y0 > y1:
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

    def to_list(self):
        return [self.x0, self.y0, self.x1, self.y1]

    def __repr__(self):
        return "Bounds[({:3f}, {:3f}), ({:3f}, {:3f})]".format(self.x0, self.y0, self.x1, self.y1)


class Object(object):
    def __init__(self, name, confidence, bounds, image):
        """
        Create Object Object

        Parameters
        ----------
        name: str
        confidence: float
        bounds: Bounds
        image: AbstractImage
        """
        self._name = name
        self._confidence = confidence
        self._bounds = bounds
        self._image = image

    @property
    def name(self):
        """
        Returns
        -------
        name: str
            Name of Person
        """
        return self._name

    @property
    def confidence(self):
        """
        Returns
        -------
        confidence: float
            Name Confidence
        """
        return self._confidence

    @property
    def bounds(self):
        """
        Face Bounds (Relative to Image)

        Returns
        -------
        bounds: Bounds
            Object Bounding Box
        """
        return self._bounds

    @property
    def image(self):
        """
        Returns
        -------
        image: AbstractImage
        """
        return self._image

    @property
    def position(self):
        return self.image.position_2d(self.bounds.center)

    def __repr__(self):
        return "{}[{:4.0%}] '{}'".format(self.__class__.__name__, self.confidence, self.name)


class ObjectDetectionClient(object):
    def __init__(self, target):
        # type: (ObjectDetectionTarget) -> ObjectDetectionClient
        self._target = target
        self._address = target.value

    @property
    def target(self):
        # type: () -> ObjectDetectionTarget
        return self._target

    def classify(self, image):
        # type: (AbstractImage) -> List[Object]
        try:
            sock = socket()
            sock.connect(self._address)

            sock.sendall(np.array(image.image.shape, np.uint32))
            sock.sendall(image.image)

            response_length = np.frombuffer(sock.recv(4), np.uint32)[0]
            response = [self._obj_from_dict(info, image) for info in json.loads(self._receive_all(sock, response_length).decode())]

            return response
        except socket_error:
            raise RuntimeError("Couldn't connect to Object Detection Service, "
                               "are you sure you're running this pepper_tensorflow service?")

    @staticmethod
    def _obj_from_dict(info, image):
        box = info['box']
        return Object(info['name'], info['score'], Bounds(box[1], box[0], box[3], box[2]), image)

    @staticmethod
    def _receive_all(sock, n):
        buffer = bytearray()
        while len(buffer) < n:
            buffer.extend(sock.recv(4096))
        return buffer
