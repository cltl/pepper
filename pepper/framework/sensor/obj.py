from pepper.framework.abstract import AbstractImage
from pepper.framework.util import Bounds, spherical2cartesian
from pepper import ObjectDetectionTarget

import numpy as np

from socket import socket, error as socket_error
from random import getrandbits
import json

from typing import List, Tuple, Dict


class Object(object):
    """
    'Object' object

    Parameters
    ----------
    name: str
        Name of Object
    confidence: float
        Object Name & Bounds Confidence
    bounds: Bounds
        Bounds in Image Space
    image: AbstractImage
        Image from which Object was Recognised
    """

    def __init__(self, name, confidence, bounds, image):
        # type: (str, float, Bounds, AbstractImage) -> None
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

    @classmethod
    def from_json(cls, data, image):
        # type: (Dict, AbstractImage) -> Object
        return cls(data["name"], data["confidence"], Bounds.from_json(data["bounds"]), image)

    @property
    def id(self):
        # type: () -> int
        """
        Object ID

        Returns
        -------
        id: int
        """
        return self._id

    @property
    def name(self):
        # type: () -> str
        """
        Object Name

        Returns
        -------
        name: str
            Name of Person
        """
        return self._name

    @property
    def confidence(self):
        # type: () -> float
        """
        Object Confidence

        Returns
        -------
        confidence: float
            Object Name & Bounds Confidence
        """
        return self._confidence

    @property
    def time(self):
        # type: () -> float
        """
        Time of Observation

        Returns
        -------
        time: float
        """
        return self.image.time

    @property
    def image_bounds(self):
        # type: () -> Bounds
        """
        Object Bounds in Image Space {x: [0, 1], y: [0, 1]}

        Returns
        -------
        bounds: Bounds
            Object Bounding Box in Image Space
        """
        return self._image_bounds

    @property
    def bounds(self):
        # type: () -> Bounds
        """
        Object Bounds in View Space {x: [-pi, +pi], y: [0, pi]}

        Returns
        -------
        bounds: Bounds
            Object Bounding Box in View Space
        """
        return self._bounds

    @property
    def image(self):
        # type: () -> AbstractImage
        """
        Image associated with the observation of this Object

        Returns
        -------
        image: AbstractImage
        """
        return self._image

    @property
    def direction(self):
        # type: () -> Tuple[float, float]
        """
         Direction of Object in View Space (equivalent to self.bounds.center)

        Returns
        -------
        direction: float, float
            Direction of Object in View Space
        """
        return self._direction

    @property
    def depth(self):
        # type: () -> float
        """
        Distance from Camera to Object

        Returns
        -------
        depth: float
            Distance from Camera to Object
        """
        return self._depth

    @property
    def position(self):
        # type: () -> Tuple[float, float, float]
        """
        Position of Object in Cartesian Coordinates (x,y,z), Relative to Camera

        Returns
        -------
        position: Tuple[float, float, float]
            Position of Object in Cartesian Coordinates (x,y,z)
        """
        return self._position

    @property
    def bounds3D(self):
        # type: () -> List[Tuple[float, float, float]]
        """
        3D bounds (for visualisation) [x,y,z]*4

        Returns
        -------
        bounds3D: List[Tuple[float, float, float]]
            3D bounds (for visualisation) [x,y,z]*4
        """
        return self._bounds3D

    def distance_to(self, obj):
        # type: (Object) -> float
        """
        Distance from this Object to obj

        Parameters
        ----------
        obj: Object

        Returns
        -------
        distance: float
        """
        return np.sqrt(
            (self.position[0] - obj.position[0])**2 +
            (self.position[1] - obj.position[1])**2 +
            (self.position[2] - obj.position[2])**2
        )

    def dict(self):
        # type: () -> Dict
        """
        Object to Dictionary

        Returns
        -------
        dict: Dict
            Dictionary representation of Object
        """

        return {
            "name": self.name,
            "confidence": self.confidence,
            "bounds": self.image_bounds.dict(),
            "image": self.image.hash
        }

    def json(self):
        # type: () -> str
        """
        Object to JSON

        Returns
        -------
        json: JSON representation of Object
        """
        return json.dumps(self.dict())

    def _calculate_object_depth(self):
        # type: () -> float
        """
        Calculate Distance of Object to Camera
        Take the median of all valid depth pixels...

        # TODO: Improve Depth Calculation

        Returns
        -------
        depth: float
        """
        depth_map = self.image.get_depth(self._image_bounds)
        depth_map_valid = depth_map != 0

        if np.sum(depth_map_valid):
            return np.median(depth_map[depth_map_valid])
        else:
            return 0.0

    def _calculate_bounds(self):
        # type: () -> Bounds
        """
        Calculate View Space Bounds from Image Space Bounds

        Returns
        -------
        bounds: Bounds
            Bounds in View Space
        """
        x0, y0 = self._image.get_direction((self._image_bounds.x0, self._image_bounds.y0))
        x1, y1 = self._image.get_direction((self._image_bounds.x1, self._image_bounds.y1))
        return Bounds(x0, y0, x1, y1)

    def _calculate_bounds_3D(self):
        # type: () -> List[List[float]]
        """
        Calculate 3D Bounds (for visualisation)

        Returns
        -------
        bounds_3D: List[List[float]]
        """
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
