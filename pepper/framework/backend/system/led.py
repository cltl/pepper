from pepper.framework.abstract.led import AbstractLed, Led
from typing import List, Tuple


class SystemLed(AbstractLed):
    def set(self, leds, rgb, duration):
        # type: (List[Led], Tuple[float, float, float], float) -> None
        pass

    def off(self, leds):
        # type: (List[Led]) -> None
        pass
