from enum import Enum
from typing import List, Tuple


class Led(Enum):
    LeftEarLeds = 0
    LeftEarLed1 = 1
    LeftEarLed2 = 2
    LeftEarLed3 = 3
    LeftEarLed4 = 4
    LeftEarLed5 = 5
    LeftEarLed6 = 6
    LeftEarLed7 = 7
    LeftEarLed8 = 8
    LeftEarLed9 = 9
    LeftEarLed10 = 10
    RightEarLeds = 11
    RightEarLed1 = 12
    RightEarLed2 = 13
    RightEarLed3 = 14
    RightEarLed4 = 15
    RightEarLed5 = 16
    RightEarLed6 = 17
    RightEarLed7 = 18
    RightEarLed8 = 19
    RightEarLed9 = 20
    RightEarLed10 = 21
    LeftFaceLeds = 22
    LeftFaceLed1 = 23
    LeftFaceLed2 = 24
    LeftFaceLed3 = 25
    LeftFaceLed4 = 26
    LeftFaceLed5 = 27
    LeftFaceLed6 = 28
    LeftFaceLed7 = 29
    LeftFaceLed8 = 30
    RightFaceLeds = 31
    RightFaceLed1 = 32
    RightFaceLed2 = 33
    RightFaceLed3 = 34
    RightFaceLed4 = 35
    RightFaceLed5 = 36
    RightFaceLed6 = 37
    RightFaceLed7 = 38
    RightFaceLed8 = 39


class AbstractLed(object):
    def set(self, leds, rgb, duration):
        # type: (List[Led], Tuple[float, float, float], float) -> None
        raise NotImplementedError()

    def off(self, leds):
        # type: (List[Led]) -> None
        raise NotImplementedError()
