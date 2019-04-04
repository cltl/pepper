from pepper.language import Chat
from pepper.framework import AbstractIntention
from pepper.framework.sensor.location import Location
from pepper.framework.sensor.face import Face
from pepper.framework.sensor.obj import Object

import numpy as np

from sklearn.cluster import DBSCAN

from collections import deque
from datetime import datetime
from time import time

from typing import List, Iterable, Dict, Tuple, Optional, Deque


class Context(object):

    OBSERVATION_TIMEOUT = 60

    _people = None  # type: Dict[str, Tuple[Face, float]]
    _objects = None  # type: Dict[str, Observations]

    def __init__(self):
        self._chats = []
        self._chatting = False

        self._people = {}
        self._objects = {}
        self._intention = None

        self._location = Location()

    @property
    def chats(self):
        # type: () -> List[Chat]
        """
        Returns
        -------
        chats: list of Chat
            List of all Chats that were held during current session
        """
        return self._chats

    @property
    def chatting(self):
        return self._chatting

    @property
    def chat(self):
        # type: () -> Optional[Chat]
        return self.chats[-1] if self.chatting else None

    @property
    def datetime(self):     # When
        # type: () -> datetime
        """
        Returns
        -------
        datetime: datetime
            Current Date and Time
        """
        return datetime.now()

    @property
    def location(self):     # Where
        # type: () -> Location
        """
        Returns
        -------
        location: Location
            Current Location
        """
        return self._location

    @property
    def people(self):      # Who
        # type: () -> List[Face]
        """
        Returns
        -------
        people: list of Face
            List of People Seen within Observation Timeout
        """
        return [person for person, t in self._people.values() if (time() - t) < Context.OBSERVATION_TIMEOUT]

    @property
    def all_people(self):
        # type: () -> List[Face]
        """
        Returns
        -------
        people: list of Face
            List of All People Seen within Observation Timeout
        """
        return [person for person, t in self._people.values()]

    @property
    def objects(self):      # What
        # type: () -> List[Object]
        """
        Returns
        -------
        objects: list of Object
            List of Objects Seen within
        """

        objects = []

        for observations in self._objects.values():
            for obj in observations.get():
                objects.append(obj)

        return objects

    @property
    def all_objects(self):
        # type: () -> List[Object]
        """
        Returns
        -------
        objects: list of Object
            List of All Objects Seen
        """
        return self.objects

    @property
    def intention(self):    # Why
        # type: () -> Optional[AbstractIntention]
        """
        Returns
        -------
        intention: AbstractIntention
            Current Intention
        """
        return self._intention

    @intention.setter
    def intention(self, intention):
        # type: (AbstractIntention) -> None
        """
        Parameters
        ----------
        intention: AbstractIntention
        """
        self._intention = intention

    def add_objects(self, objects):
        # type: (Iterable[Object]) -> None
        """
        Parameters
        ----------
        objects: list of Object
            List of Objects
        """
        for obj in objects:
            if obj.name not in self._objects:
                self._objects[obj.name] = Observations()

            self._objects[obj.name].add(obj)

    def add_people(self, people):
        # type: (Iterable[Face]) -> None
        """
        Parameters
        ----------
        people: list of Face
            List of People
        """
        for person in people:
            self._people[person.name] = (person, time())

    def start_chat(self, speaker):
        self._chatting = True
        self._chats.append(Chat(speaker, self))

    def stop_chat(self):
        self._chatting = False

    @staticmethod
    def _cluster_objects(objects):
        pass


class Observations(object):
    def __init__(self, max_samples=100, max_distance=0.1, min_samples=10, timeout=5.0):
        self._deque = deque(maxlen=max_samples)
        self._min_samples = min_samples
        self._max_distance = max_distance
        self._timeout = timeout

    def add(self, obj):
        # type: (Object) -> None
        self._deque.appendleft((obj, time()))

        # TODO: add object gone observation!

    def get(self):
        # type: () -> List[Object]
        objects = [obj for obj, t in self._deque if time() - t < self._timeout]  # type: List[Object]

        if not objects:
            return []

        positions = np.array([obj.position for obj in objects])

        cluster = DBSCAN(eps=self._max_distance, min_samples=self._min_samples)
        cluster.fit(positions)

        result = []

        for label in np.unique(cluster.labels_):
            if label >= 0:  # If Label is not Noise
                result.append(objects[np.argwhere(cluster.labels_ == label)[0][0]])

        return result



