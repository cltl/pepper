from pepper.language import Chat
from pepper.framework import AbstractIntention, AbstractImage
from pepper.framework.sensor.location import Location
from pepper.framework.sensor.face import Face
from pepper.framework.sensor.obj import Object

import numpy as np

from sklearn.cluster import DBSCAN

from collections import deque
from random import getrandbits
from datetime import datetime
from time import time

from typing import List, Iterable, Dict, Tuple, Optional, Deque

from threading import Lock


class Context(object):

    OBSERVATION_TIMEOUT = 60

    _people = None  # type: Dict[str, Tuple[Face, float]]
    _objects = None # type: Observations

    def __init__(self):

        self._id = getrandbits(128)

        self._chats = []
        self._chatting = False

        self._people = {}
        self._objects = Observations()
        self._intention = None

        self._location = Location()

    @property
    def id(self):
        return self._id

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
        return self._objects.instances

    @property
    def all_objects(self):
        # type: () -> List[Object]
        """
        Returns
        -------
        objects: list of Object
            List of All Objects Seen
        """
        return self._objects.instances

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
        # type: (List[Object]) -> None
        """
        Parameters
        ----------
        objects: list of Object
            List of Objects
        """
        if objects:
            self._objects.add_observations(objects[0].image, objects)

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


class Observations:
    def __init__(self):
        self._object_observations = {}

    @property
    def instances(self):
        instances = []

        for object_observations in self._object_observations.values():
            instances.extend(object_observations.instances)

        return instances

    def add_observations(self, image, objects):
        for obj in objects:
            if obj.name not in self._object_observations:
                self._object_observations[obj.name] = ObjectObservations()
            self._object_observations[obj.name].add_observation(obj)

        for object_observations in self._object_observations.values():
            object_observations.update_view(image)


class ObjectObservations:

    EPSILON = 0.4
    MIN_SAMPLES = 5
    MAX_SAMPLES = 50
    OBSERVATION_TIMEOUT = 2

    def __init__(self):
        self._observations = []
        self._instances = []

    @property
    def instances(self):
        return self._instances

    def update_view(self, image):

        # Go through observations oldest to newest
        for observation in self._observations[::-1]:

            # If observation could be done with current view
            if image.bounds.contains(observation.bounds.center):

                current_depth = image.get_depth(observation.image_bounds)
                current_depth = np.min(current_depth[current_depth != 0], initial=np.inf)

                # If nothing is occluding her view
                if current_depth > observation.depth - self.EPSILON:

                    # Check if recent observation of this object is made
                    found_recent_observation = False
                    for obs in self._observations:
                        if time() - obs.image.time > self.OBSERVATION_TIMEOUT:
                            break

                        if image.bounds.contains(obs.bounds.center):
                            found_recent_observation = True
                            break

                    # If no recent observation has been found -> remove one old observation
                    if not found_recent_observation:
                        self._observations.remove(observation)
                        break

    def add_observation(self, obj):
        self._observations.append(obj)

        instances = []
        removal = []

        # Cluster to find Object Instances
        cluster = DBSCAN(eps=self.EPSILON, min_samples=self.MIN_SAMPLES)
        cluster.fit([obj.position for obj in self._observations])

        unique_labels = np.unique(cluster.labels_)

        # Find oldest instance per group add to Instances
        for label in unique_labels:

            group_indices = np.argwhere(cluster.labels_ == label).ravel()

            if label != -1:  # Skip Noisy Observations
                newest_instance = self._observations[group_indices[-1]]
                instances.append(newest_instance)

            removal.extend(group_indices[:-self.MAX_SAMPLES])

        self._instances = instances
        self._observations = [self._observations[i] for i in range(len(self._observations)) if i not in removal]




