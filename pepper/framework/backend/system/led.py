from pepper.framework.abstract.led import AbstractLed, Led
from typing import List, Tuple


class SystemLed(AbstractLed):
    """Control Robot LEDs"""

    def set(self, leds, rgb, duration):
        # type: (List[Led], Tuple[float, float, float], float) -> None
        """
        Set LEDs to Particular color (interpolating from its current color in 'duration' time)

        Parameters
        ----------
        leds: List[Led]
            Which LEDs are affected
        rgb: Tuple[float, float, float]
            Which color to turn
        duration: float
            How long to take switching this color
        """
        pass

    def off(self, leds):
        # type: (List[Led]) -> None
        """
        Switch LEDs off

        Parameters
        ----------
        leds: List[Led]
            Which LEDs are affected
        """
        pass
