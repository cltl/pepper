from enum import Enum


class Leds(Enum):
    RIGHT_FACE_LEDS = "RightFaceLeds{}"
    LEFT_FACE_LEDS = "LeftFaceLeds{}"


class Led(object):
    def __init__(self, session):
        """
        Control Pepper's Led Lights

        Parameters
        ----------
        session: qi.Session
            Session in which to control the leds
        """

        self._session = session
        self._service = session.service("ALLeds")

    @property
    def session(self):
        """
        Returns
        -------
        session: qi.Session
            Session in which to control the leds
        """

        return self._session

    @property
    def service(self):
        """
        Returns
        -------
        service
            ALLeds Service
        """
        return self._service

    def set(self, rgb):
        """
        Set led color

        Parameters
        ----------
        led: Leds
            Led to control
        rgb: list of float
            Led RGB value
        """
        for i, color in enumerate(["Red", "Green", "Blue"]):
            for led in ["RightFaceLeds{}","LeftFaceLeds{}"]:
                self.service.setIntensity(led.format(color), rgb[i])

    def reset(self, led):
        """
        Reset led color

        Parameters
        ----------
        led: Leds
         Led to control
        """
        for color in ["Red", "Green", "Blue"]:
            self.service.reset(led.value.format(color))
