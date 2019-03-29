from pepper.framework.abstract.led import AbstractLed, Led
from typing import List, Tuple


class NaoqiLed(AbstractLed):
    def __init__(self, session):
        self._led = session.service("ALLeds")

    def set(self, leds, rgb, duration):
        # type: (List[Led], Tuple[float, float, float], float) -> None

        for led in leds:
            self._led.fade(led.name, rgb, duration)

    def off(self, leds):
        # type: (List[Led]) -> None
        for led in leds:
            self._led.off(led.name)
