from typing import Tuple


class AbstractMotion(object):
    def look(self, direction):
        # type: (Tuple[float, float]) -> None
        pass