from enum import Enum
from typing import List, Tuple


class Led(Enum):
    pass


class LeftEarLed(Led):
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
    
    
class RightEarLed(Led):
    RightEarLed1 = 1
    RightEarLed2 = 2
    RightEarLed3 = 3
    RightEarLed4 = 4
    RightEarLed5 = 5
    RightEarLed6 = 6
    RightEarLed7 = 7
    RightEarLed8 = 8
    RightEarLed9 = 9
    RightEarLed10 = 10
    

class LeftFaceLed(Led):
    LeftFaceLed1 = 1
    LeftFaceLed2 = 2
    LeftFaceLed3 = 3
    LeftFaceLed4 = 4
    LeftFaceLed5 = 5
    LeftFaceLed6 = 6
    LeftFaceLed7 = 7
    LeftFaceLed8 = 8
    
    
class RightFaceLed(Led):
    RightFaceLed1 = 1
    RightFaceLed2 = 2
    RightFaceLed3 = 3
    RightFaceLed4 = 4
    RightFaceLed5 = 5
    RightFaceLed6 = 6
    RightFaceLed7 = 7
    RightFaceLed8 = 8


class AbstractLed(object):
    def set(self, leds, rgb, duration):
        # type: (List[Led], Tuple[float, float, float], float) -> None
        raise NotImplementedError()

    def off(self, leds):
        # type: (List[Led]) -> None
        raise NotImplementedError()
