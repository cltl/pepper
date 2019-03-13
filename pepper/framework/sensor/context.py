from pepper.language import Chat
from pepper.framework import AbstractIntention
from pepper.framework.sensor.location import Location
from .face import Face
from .obj import Object

from datetime import datetime
from time import time

from typing import List, Iterable, Dict, Tuple, Optional


class Context(object):

    OBSERVATION_TIMEOUT = 120

    _people = None  # type: Dict[str, Tuple[Face, float]]
    _objects = None  # type: Dict[str, Tuple[Object, float]]

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
            List of People Seen
        """
        return [person for person, t in self._people.values() if (time() - t) < Context.OBSERVATION_TIMEOUT]

    @property
    def objects(self):      # What
        # type: () -> List[Object]
        """
        Returns
        -------
        objects: list of Object
            List of Objects Seen
        """
        return [obj for obj, t in self._objects.values() if (time() - t) < Context.OBSERVATION_TIMEOUT]

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
            self._objects[obj.name] = (obj, time())

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
