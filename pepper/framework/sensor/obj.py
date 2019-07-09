from pepper.framework.abstract import AbstractImage
from pepper.framework.util import Bounds, spherical2cartesian
from pepper import ObjectDetectionTarget

import numpy as np

from socket import socket, error as socket_error
from random import getrandbits
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

        self._id = getrandbits(128)

        self._name = name
        self._confidence = confidence
        self._image_bounds = bounds
        self._image = image

        # Calculate Position in 2D Angular Space (Phi, Theta)
        self._bounds = self._calculate_bounds()
        self._direction = self.bounds.center

        # Calculate Position in 3D Space (Relative to Robot)
        self._depth = self._calculate_object_depth()
        self._position = spherical2cartesian(self._direction[0], self._direction[1], self._depth)
        self._bounds3D = self._calculate_bounds_3D()

    @property
    def id(self):
        return self._id

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
    def time(self):
        return self.image.time

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
    def direction(self):
        return self._direction

    @property
    def position(self):
        return self._position

    @property
    def depth(self):
        return self._depth

    @property
    def bounds3D(self):
        return self._bounds3D

    def _calculate_object_depth(self):
        depth_map = self.image.get_depth(self._image_bounds)
        depth_map_valid = depth_map != 0

        if np.sum(depth_map_valid):
            return np.median(depth_map[depth_map_valid])
        else:
            return 0.0

    def _calculate_bounds(self):
        x0, y0 = self._image.direction((self._image_bounds.x0, self._image_bounds.y0))
        x1, y1 = self._image.direction((self._image_bounds.x1, self._image_bounds.y1))
        return Bounds(x0, y0, x1, y1)

    def _calculate_bounds_3D(self):
        return [
            spherical2cartesian(self._bounds.x0, self._bounds.y0, self._depth),
            spherical2cartesian(self._bounds.x0, self._bounds.y1, self._depth),
            spherical2cartesian(self._bounds.x1, self._bounds.y1, self._depth),
            spherical2cartesian(self._bounds.x1, self._bounds.y0, self._depth),
        ]

    def __repr__(self):
        return "{}({}, {:3.0%})".format(self.__class__.__name__, self.name, self.confidence)


class ObjectDetectionClient(object):
    def __init__(self, target):
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
