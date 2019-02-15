from pepper.language import Chat
from .face import Face
from .obj import Object

from datetime import datetime

from typing import List


class Context(object):
    def __init__(self):
        self._chats = []

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
    def place(self):        # Where
        raise NotImplementedError()

    @property
    def persons(self):      # Who
        # type: () -> List[Face]
        raise NotImplementedError()

    @property
    def objects(self):      # What
        # type: () -> List[Object]
        raise NotImplementedError()

    @property
    def intention(self):    # Why
        raise NotImplementedError()


if __name__ == '__main__':
    print(Context().place)
