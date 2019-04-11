from pepper.framework.abstract import AbstractImage
from pepper.framework.util import Bounds
from pepper import ObjectDetectionTarget

import numpy as np

from socket import socket, error as socket_error
import json

from typing import List


class Object(object):
    def __init__(self, name, confidence, bounds, image):
        """
        Create Object Object

        Parameters
        ----------
        name: str
            Name of Object
        confidence: float
            Confidence of Object Name & Position
        bounds: Bounds
            Bounds in Image Space
        image: AbstractImage
            Image from which Object was Recognised
        """
        self._name = name
        self._confidence = confidence
        self._image_bounds = bounds
        self._image = image

        x0, y0 = image.position_2d((self._image_bounds.x0, self._image_bounds.y0))
        x1, y1 = image.position_2d((self._image_bounds.x1, self._image_bounds.y1))
        self._bounds = Bounds(x0, y0, x1, y1)

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
    def image_bounds(self):
        """
        Object Bounds (Relative to Image)

        Returns
        -------
        bounds: Bounds
            Object Bounding Box
        """
        return self._image_bounds

    @property
    def bounds(self):
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
        return self.image.position_2d(self.image_bounds.center)

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
