from typing import Tuple


class AbstractMotion(object):

    def look(self, direction, speed=1):
        # type: (Tuple[float, float], float) -> None
        pass

    def point(self, direction, speed=1):
        # type: (Tuple[float, float], float) -> None
        pass
