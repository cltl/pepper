"""
Context
=======

"""

from pepper.language import Chat
from pepper.framework import AbstractImage
from pepper.framework.sensor.location import Location
from pepper.framework.sensor.face import Face
from pepper.framework.sensor.obj import Object

from pepper.knowledge.objects import OBJECT_INFO

import numpy as np

from sklearn.cluster import DBSCAN

from random import getrandbits
from datetime import datetime
from time import time

from typing import List, Iterable, Dict, Tuple, Optional


class Context(object):
    """
    Context Object

    Contains Awareness for People, Objects & Conversations
    """

    OBSERVATION_TIMEOUT = 60

    _people = None  # type: Dict[str, Tuple[Face, float]]
    _objects = None  # type: Observations

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
        # type: () -> int
        """
        ID

        Returns
        -------
        id: int
        """
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
        # type: () -> bool
        """
        Returns True when a Chat is happening

        Returns
        -------
        chatting: bool
        """
        return self._chatting

    @property
    def chat(self):
        # type: () -> Optional[Chat]
        """
        The Current Chat, if any

        Returns
        -------
        chat: Optional[Chat]
        """
        return self.chats[-1] if self.chatting else None

    @property
    def datetime(self):     # When
        # type: () -> datetime
        """
        The Current Date & Time

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
        The Current Location

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
        People seen within Observation Timeout

        Returns
        -------
        people: list of Face
            List of People seen within Observation Timeout
        """
        return [person for person, t in self._people.values() if (time() - t) < Context.OBSERVATION_TIMEOUT]

    @property
    def all_people(self):
        # type: () -> List[Face]
        """
        People seen since beginning of Context

        Returns
        -------
        people: list of Face
            List of all People seen since beginning of Context
        """
        return [person for person, t in self._people.values()]

    @property
    def objects(self):      # What
        # type: () -> List[Object]
        """
        Objects seen within Observation Timeout

        Returns
        -------
        objects: list of Object
            List of Objects seen within Observation Timeout
        """
        return self._objects.instances

    @property
    def all_objects(self):
        # type: () -> List[Object]
        """
        Objects seen since beginning of Context

        Returns
        -------
        objects: list of Object
            List of all Objects since beginning of Context
        """
        return self._objects.instances

    def add_objects(self, objects):
        # type: (List[Object]) -> None
        """
        Add Object Observations to Context

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
        Add People Observations to Context

        Parameters
        ----------
        people: list of Face
            List of People
        """
        for person in people:
            self._people[person.name] = (person, time())

    def start_chat(self, speaker):
        # type: (str) -> None
        """
        Start Chat with Speaker

        Parameters
        ----------
        speaker: str
            Name of Speaker
        """
        self._chatting = True
        self._chats.append(Chat(speaker, self))

    def stop_chat(self):
        # type: () -> None
        """Stop Chat"""
        self._chatting = False


class Observations:
    """
    Object Observations

    Object to track of which objects have been seen and where. Groups Object Observations based on location,
    to guess which observations are in fact of the same object. Each Object Class is handled in ObjectObservations.
    """

    def __init__(self):
        # type: () -> None
        self._object_observations = {}

    @property
    def instances(self):
        # type: () -> List[Object]
        """
        Get individual object instances, based on observations

        Returns
        -------
        instances: List[Object]
        """
        instances = []

        for object_observations in self._object_observations.values():
            instances.extend(object_observations.instances)

        return instances

    def add_observations(self, image, objects):
        # type: (AbstractImage, List[Object]) -> None
        """
        Add Object Observations and figure out with which Object Instance they correspond

        Parameters
        ----------
        image: AbstractImage
        objects: List[Object]
        """
        for obj in objects:
            if obj.name not in self._object_observations:
                self._object_observations[obj.name] = ObjectObservations(obj.name)
            self._object_observations[obj.name].add_observation(obj)

        for object_observations in self._object_observations.values():
            object_observations.update_view(image)


class ObjectObservations:
    """
    Object Observations for a particular Object Class
    """

    EPSILON = 0.2  # Distance in Metres within which observations are considered one single instance

    MIN_SAMPLES = 5  # Minimum number of observations for an instance
    MAX_SAMPLES = 50  # Maximum number of observations for an instance
    INSTANCE_TIMEOUT = 120  # Time in seconds without observation after which an instance no longer exists

    MIN_SAMPLES_MOVING = 3
    MAX_SAMPLES_MOVING = 8
    INSTANCE_TIMEOUT_MOVING = 30

    OBSERVATION_BOUNDS_AREA_THRESHOLD = 0.9  # If exceeded, observation is treated as a label for the scene instead
    OBSERVATION_TIMEOUT = 2  # Time in seconds for an observation to be considered 'recent'

    def __init__(self, name):
        # type: () -> None
        self._name = name
        self._moving = OBJECT_INFO[name]['moving'] if name in OBJECT_INFO else False

        self._min_samples = self.MIN_SAMPLES_MOVING if self._moving else self.MIN_SAMPLES
        self._max_samples = self.MAX_SAMPLES_MOVING if self._moving else self.MAX_SAMPLES
        self._instance_timeout = self.INSTANCE_TIMEOUT_MOVING if self._moving else self.INSTANCE_TIMEOUT

        self._observations = []
        self._instances = []

    @property
    def instances(self):
        # type: () -> List[Object]
        """
        Get individual object instances for this Object Class

        Returns
        -------
        instances: List[Object]
        """
        return self._instances

    def update_view(self, image):
        # type: (AbstractImage) -> None
        """
        Update Object Instances with Current Image

        Remove Observations one by one, when they are not longer where expected

        Parameters
        ----------
        image: AbstractImage
        """

        # If observation is a scene descriptor instead of an actual object, override clustering and use single instance
        if len(self._instances) == 1 and self._instances[0].image_bounds.area > self.OBSERVATION_BOUNDS_AREA_THRESHOLD:
            return

        # Limit observations & Instances to be within INSTANCE TIMEOUT
        self._observations = [obs for obs in self._observations if time() - obs.time < self._instance_timeout]
        self._instances = [ins for ins in self._instances if time() - ins.time < self._instance_timeout]

        # Go through observations oldest to newest
        for observation in self._observations[::-1]:

            # If observation could be done with current view
            if image.bounds.contains(observation.bounds.center):

                # Get Current Depth at Object Bounds to see if something might be occluding her view
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

    def add_observation(self, observation):
        """
        Add Observation of object with this Object Class

        Cluster Object Observations to figure out Object Instances

        Parameters
        ----------
        observation: Object
        """

        # If observation is a scene descriptor instead of an actual object, override clustering and use single instance
        if observation.image_bounds.area > self.OBSERVATION_BOUNDS_AREA_THRESHOLD:
            self._instances = [observation]
            return

        # Append Object Observation to all Observations
        self._observations.append(observation)

        # Get Positions of all Observations
        positions = [observation.position for observation in self._observations]

        instances = []
        removal = []

        # Cluster to find Object Instances
        cluster = DBSCAN(eps=self.EPSILON, min_samples=self._min_samples)
        cluster.fit(positions)

        unique_labels = np.unique(cluster.labels_)

        # Find newest instance per group add to Instances
        for label in unique_labels:

            group_indices = np.argwhere(cluster.labels_ == label).ravel()

            if label != -1:  # Skip Noisy Observations
                newest_instance = self._observations[group_indices[-1]]
                instances.append(newest_instance)

            removal.extend(group_indices[:-self._max_samples])

        self._instances = instances

        # Limit amount of stored observations
        self._observations = [self._observations[i] for i in range(len(self._observations)) if i not in removal]
