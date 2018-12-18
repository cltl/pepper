from pepper.language import Chat
from pepper.framework.sensor import Object, Face

import numpy as np

from datetime import datetime
from time import time
import geocoder

from collections import deque

from typing import Optional, Iterable, Deque, Tuple


class Events(object):

    # TODO: Add Attention Span
    # TODO: Add Face/Object lost event
    # TODO: Add Absolute Bounds, Relative to Robot's Position

    _images = None  # type: Deque[Tuple[np.ndarray, float]]
    _faces = None  # type: Deque[Tuple[Face, float]]
    _objects = None  # type: Deque[Tuple[Object, float]]
    _chat = None  # type: Optional[Chat]

    def __init__(self):
        self._images = deque()
        self._faces = deque()
        self._objects = deque()

        self._chat = None

    @property
    def chat(self):
        # type: () -> Optional[Chat]
        """
        Get Current Chat (if Any)

        Returns
        -------
        chat: Chat or None
        """
        return self._chat

    @property
    def images(self):
        return [image for image, t in self._images]

    @property
    def faces(self):
        # type: () -> Iterable[Face]
        """
        Returns
        -------
        faces: list of Face
        """
        return [face for face, t in self._faces]

    @property
    def objects(self):
        # type: () -> Iterable[Object]
        """
        Get Current Objects

        Returns
        -------
        objects: list of Object
        """
        return [obj for obj, t in self._objects]

    @property
    def datetime(self):
        # type: () -> datetime
        """
        Get Current Date and Time

        Returns
        -------
        datetime: datetime
        """
        return datetime.now()

    @property
    def ip(self):
        # type: () -> str
        """
        Get Current Internet Provider Host Name

        Returns
        -------
        provider: str
        """
        return geocoder.ip('me').ip

    def add_objects(self, objects):
        self._objects.extend((obj, time()) for obj in objects)

    def update(self):
        # TODO: Remove Outdated Objects
        raise NotImplementedError()
