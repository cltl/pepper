from pepper.language import Chat
from pepper.framework import AbstractIntention, AbstractImage
from pepper.framework.sensor.location import Location
from pepper.framework.sensor.face import Face
from pepper.framework.sensor.obj import Object

import numpy as np

from sklearn.cluster import DBSCAN

from collections import deque
from datetime import datetime
from time import time

from typing import List, Iterable, Dict, Tuple, Optional, Deque

from threading import Lock


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

        image = None

        if objects:
            # Create New Observation Classes if Necessary
            for obj in objects:

                image = obj.image

                if obj.name not in self._objects:
                    self._objects[obj.name] = Observations()

            # Add Observations for each Object Type
            if image:
                for name, observations in self._objects.items():
                    observations.add(image, [obj for obj in objects if obj.name == name])

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

    LOCK = Lock()

    def __init__(self, epsilon=0.1, min_samples=5, max_samples=10, timeout=5):

        self._epsilon = epsilon
        self._min_samples = min_samples
        self._max_samples = max_samples
        self._timeout = timeout

        self._observations = deque()
        self._unique_objects = []

    @property
    def observations(self):
        # type: () -> Deque[Tuple[Object, float]]
        return self._observations

    @property
    def objects(self):
        # type: () -> List[Object]
        return self._unique_objects

    def get(self):
        # type: () -> List[Object]
        return self._unique_objects

    def add(self, image, objects):
        # type: (AbstractImage, List[Object]) -> None

        with self.LOCK:

            # 1. Add Objects to Observations
            for obj in objects:
                self._observations.appendleft((obj, time()))

            if self._observations:

                # 2. Cluster Observations
                cluster = DBSCAN(self._epsilon, self._min_samples)
                cluster.fit(np.array([obj.position for obj, t in self.observations]))

                groups = [(label, np.argwhere(cluster.labels_ == label).ravel()) for label in np.unique(cluster.labels_)]

                # 3. Prune Observations
                observations = []
                unique_objects = []

                for group, indices in groups:

                    # Add most recent observation of each Unique Objects to List
                    if group != -1:
                        unique_objects.append(self._observations[indices[0]])

                    for i, index in enumerate(indices):

                        if i >= self._max_samples:
                            break

                        sample, sample_time = self.observations[index]

                        if group != -1:
                            # If Sample should be visible now -> Add only if currently visible
                            if time() - sample_time > self._timeout and image.bounds.contains(sample.position):
                                for obj in objects:
                                    if obj.bounds.contains(sample.position):
                                        observations.append((sample, sample_time))
                                        break
                            else:  # if Sample is not visible atm -> Add Sample for now
                                observations.append((sample, sample_time))
                        else:
                            observations.append((sample, sample_time))

                self._observations = deque(observations)
                self._unique_objects = unique_objects

            else:
                self._unique_objects = []
