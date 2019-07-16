from typing import Tuple


class AbstractMotion(object):

    def look(self, direction, speed=1):
        # type: (Tuple[float, float], float) -> None
        """
        Look at particular direction

        Parameters
        ----------
        direction: float
        speed: float
        """
        pass

    def point(self, direction, speed=1):
        # type: (Tuple[float, float], float) -> None
        """
        Point at particular direction

        Parameters
        ----------
        direction: float
        speed: float
        """
        pass
