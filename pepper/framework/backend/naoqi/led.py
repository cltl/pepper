from pepper.framework.abstract.led import AbstractLed, Led
from pepper.framework.util import Mailbox

import qi

from typing import List, Tuple
from threading import Thread


class NAOqiLed(AbstractLed):
    """
    Control Robot LEDs

    Parameters
    ----------
    session: qi.Session
    """

    def __init__(self, session):
        # type: (qi.Session) -> None
        self._led = session.service("ALLeds")

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
        r, g, b, = rgb

        for led in leds:
            self._led.fadeRGB(led.name, float(r), float(g), float(b), float(duration))

    def off(self, leds):
        # type: (List[Led]) -> None
        """
        Switch LEDs off

        Parameters
        ----------
        leds: List[Led]
            Which LEDs are affected
        """
        for led in leds:
            self._led.off(led.name)