from pepper.framework import CameraResolution
from threading import Thread
from Queue import Queue

import numpy as np


class AbstractCamera(object):
    def __init__(self, resolution, rate, callbacks):
        """
        Abstract Camera

        Parameters
        ----------
        resolution: CameraResolution
        rate: int
        callbacks: list of callable
        """
        self._resolution = resolution
        self._width = self._resolution.value[1]
        self._height = self._resolution.value[0]

        self._rate = rate
        self._callbacks = callbacks

        self._shape = np.array([self.height, self.width, self.channels])

        self._queue = Queue()
        self._processor_thread = Thread(target=self._processor)
        self._processor_thread.daemon = True
        self._processor_thread.start()

        self._running = False

    @property
    def resolution(self):
        """
        Returns
        -------
        resolution: CameraResolution
        """
        return self._resolution

    @property
    def width(self):
        """
        Returns
        -------
        width: int
            Image width
        """
        return self._width

    @property
    def height(self):
        """
        Returns
        -------
        height: int
            Image height
        """
        return self._height

    @property
    def channels(self):
        """
        Returns
        -------
        channels: int
            Image channels
        """
        return 3

    @property
    def rate(self):
        """
        Returns
        -------
        rate: int
            Image rate
        """
        return self._rate

    @property
    def shape(self):
        """
        Returns
        -------
        shape: np.ndarray
        """
        return self._shape

    @property
    def callbacks(self):
        """
        Returns
        -------
        callbacks: list of callable
            on_image callbacks
        """
        return self._callbacks

    @callbacks.setter
    def callbacks(self, value):
        """
        Parameters
        ----------
        value: list of callable
        """
        self._callbacks = value

    def on_image(self, image):
        """
        On Image Event

        Parameters
        ----------
        image: np.ndarray
        """
        self._queue.put(image)

    def start(self):
        """Start Streaming Images from Camera"""

        self._running = True

    def stop(self):
        """Stop Streaming Images from Camera"""

        self._running = False

    def _processor(self):
        """
        Image Processor

        Calls each callback for each image, threaded, for higher image throughput
        """
        while True:
            image = self._queue.get()
            for callback in self.callbacks:
                callback(image)