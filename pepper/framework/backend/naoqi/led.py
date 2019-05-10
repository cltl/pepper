from pepper.framework.abstract.led import AbstractLed, Led
from pepper.framework.util import Mailbox
from typing import List, Tuple
from threading import Thread


class NaoqiLed(AbstractLed):
    def __init__(self, session):
        self._led = session.service("ALLeds")

    def set(self, leds, rgb, duration):
        # type: (List[Led], Tuple[float, float, float], float) -> None
        r, g, b, = rgb

        for led in leds:
            self._led.fadeRGB(led.name, float(r), float(g), float(b), float(duration))

    def off(self, leds):
        # type: (List[Led]) -> None
        for led in leds:
            self._led.off(led.name)