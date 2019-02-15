from pepper.language import Chat
from pepper.framework import AbstractIntention
from pepper.knowledge.location import Location
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
        self._people = {}
        self._objects = {}
        self._intention = None

        self._location = Location()

    @property
    def chats(self):
        # type: () -> List[Chat]
        return self._chats

    @property
    def last_chat(self):
        # type: () -> Chat
        return self._chats[-1]

    @last_chat.setter
    def last_chat(self, value):
        # type: (Chat) -> None
        self._chats.append(value)

    @property
    def datetime(self):     # When
        # type: () -> datetime
        return datetime.now()

    @property
    def location(self):     # Where
        return self._location

    @property
    def people(self):      # Who
        # type: () -> List[Face]
        return [person for person, t in self._people.values() if (time() - t) < Context.OBSERVATION_TIMEOUT]

    @property
    def objects(self):      # What
        # type: () -> List[Object]
        return [obj for obj, t in self._objects.values() if (time() - t) < Context.OBSERVATION_TIMEOUT]

    @property
    def intention(self):    # Why
        # type: () -> Optional[AbstractIntention]
        return self._intention

    @intention.setter
    def intention(self, intention):
        self._intention = intention

    def add_objects(self, objects):
        # type: (Iterable[Object]) -> None
        for obj in objects:
            self._objects[obj.name] = (obj, time())

    def add_people(self, people):
        # type: (Iterable[Face]) -> None
        for person in people:
            self._people[person.name] = (person, time())
