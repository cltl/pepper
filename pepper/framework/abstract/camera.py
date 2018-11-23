from pepper.framework.util import Mailbox
from pepper.config import CameraResolution
from pepper import logger

from threading import Thread

from collections import deque
from time import time, sleep

import numpy as np


class AbstractCamera(object):
    """
    Abstract Camera

    Parameters
    ----------
    resolution: CameraResolution
        :class:`~pepper.config.CameraResolution`
    rate: int
    callbacks: list of callable
    """

    def __init__(self, resolution, rate, callbacks):
        self._resolution = resolution
        self._width = self._resolution.value[1]
        self._height = self._resolution.value[0]

        self._rate = rate
        self._callbacks = callbacks

        self._shape = np.array([self.height, self.width, self.channels])

        self._dt_buffer = deque([], maxlen=10)
        self._true_rate = rate
        self._t0 = time()

        self._mailbox = Mailbox()
        self._processor_thread = Thread(name="CameraThread", target=self._processor)
        self._processor_thread.daemon = True
        self._processor_thread.start()

        self._running = False

        self._log = logger.getChild(self.__class__.__name__)

    @property
    def resolution(self):
        """
        Returns :class:`~pepper.config.CameraResolution`

        Returns
        -------
        resolution: CameraResolution
        """
        return self._resolution

    @property
    def width(self):
        """
        Image Width

        Returns
        -------
        width: int
            Image width
        """
        return self._width

    @property
    def height(self):
        """
        Image Height

        Returns
        -------
        height: int
            Image height
        """
        return self._height

    @property
    def channels(self):
        """
        Image (Color) Channels

        Returns
        -------
        channels: int
            Image (Color) channels
        """
        return 3

    @property
    def rate(self):
        """
        Image Rate

        Returns
        -------
        rate: int
            Image rate
        """
        return self._rate

    @property
    def true_rate(self):
        """
        Actual Image Rate

        Image rate after accounting for latency & performance realities

        Returns
        -------
        true_rate: float
            Actual Image Rate
        """
        return self._true_rate

    @property
    def shape(self):
        """
        Image Shape

        Returns
        -------
        shape: np.ndarray
            Image Shape
        """
        return self._shape

    @property
    def callbacks(self):
        """
        Get/Set :func:`~AbstractCamera.on_image` Callbacks

        Returns
        -------
        callbacks: list of callable
            on_image callbacks
        """
        return self._callbacks

    @callbacks.setter
    def callbacks(self, value):
        """
        Get/Set :func:`~AbstractCamera.on_image` Callbacks

        Parameters
        ----------
        value: list of callable
        """
        self._callbacks = value

    @property
    def running(self):
        """
        Returns whether Camera is Running

        Returns
        -------
        running: bool
        """
        return self._running

    def on_image(self, image):
        """
        On Image Event, Called for every Image captured by Camera

        Camera Modules should call this function for every frame acquired by the Camera

        Parameters
        ----------
        image: np.ndarray
        """
        self._mailbox.put(image)

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
            image = self._mailbox.get()
            if self._running:
                for callback in self.callbacks:
                    callback(image)
            self._update_dt()

    def _update_dt(self):
        t1 = time()
        self._dt_buffer.append((t1 - self._t0))
        self._t0 = t1
        self._true_rate = 1 / np.mean(self._dt_buffer)
