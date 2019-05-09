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

        # Calculate Bounds in Angle Space
        x0, y0 = image.direction((self._image_bounds.x0, self._image_bounds.y0))
        x1, y1 = image.direction((self._image_bounds.x1, self._image_bounds.y1))
        self._bounds = Bounds(x0, y0, x1, y1)

        self._direction =  self.image.direction(self.image_bounds.center)

        # Calculate Position in 3D Space (Relative to Robot)
        self._depth = self._calculate_object_depth()

        self._position = self._spherical2cartesian(self._direction[0], self._direction[1], self._depth)

        self._bounds3D = [
            self._spherical2cartesian(x0, y0, self._depth),
            self._spherical2cartesian(x0, y1, self._depth),
            self._spherical2cartesian(x1, y1, self._depth),
            self._spherical2cartesian(x1, y0, self._depth),
        ]

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

    def _spherical2cartesian(self, phi, theta, depth):
        x = depth * np.sin(theta) * np.cos(phi)
        z = depth * np.sin(theta) * np.sin(phi)
        y = depth * np.cos(theta)

        return x, y, z

    def _calculate_object_depth(self):
        depth_map = self.image.get_depth(self._image_bounds)

        kernel = 10

        depth_map_centre = depth_map[
            depth_map.shape[0]//2-kernel:depth_map.shape[0]//2+kernel,
            depth_map.shape[1]//2-kernel:depth_map.shape[1]//2+kernel
        ]

        valid = depth_map_centre != 0

        if not np.sum(valid):
            return np.min(depth_map_centre[valid], initial=100)
        else:
            return np.min(depth_map[depth_map != 0], initial=100)



    def __repr__(self):
        return "{}({}, {:3.0%})".format(self.__class__.__name__, self.name, self.confidence)


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
