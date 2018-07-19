from pepper.framework.abstract import AbstractCamera

import cv2

from threading import Thread
from time import sleep
import logging


class SystemCamera(AbstractCamera):
    def __init__(self, resolution, rate, callbacks = [], index=0):
        super(SystemCamera, self).__init__(resolution, rate, callbacks)

        self._camera = cv2.VideoCapture(index)

        self._camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self._camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)

        if not self._camera.isOpened():
            raise RuntimeError("{} could not be opened".format(self.__class__.__name__))

        self._log = logging.getLogger(self.__class__.__name__)
        self._log.debug("Booted")

        self._thread = Thread(target=self._run)
        self._thread.setDaemon(True)
        self._thread.start()

    def _run(self):
        while True:
            status, image = self._camera.read()

            if status:
                if self._running:
                    self.on_image(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            else:
                raise RuntimeWarning("{} could not fetch image".format(self.__class__.__name__))

            sleep(1. / self.rate)