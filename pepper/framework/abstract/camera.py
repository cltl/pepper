from pepper.framework.util import Mailbox, Scheduler
from pepper import CameraResolution
from pepper import logger

import numpy as np

from collections import deque
from time import time

from typing import Tuple


class AbstractImage(object):
    def __init__(self, image):
        # type: (np.ndarray) -> AbstractImage
        """
        Create (Abstract) Image Object

        Parameters
        ----------
        image: np.ndarray
        """
        self._image = image

    @property
    def image(self):
        # type: () -> np.ndarray
        """
        Image Pixels as Numpy Array

        Returns
        -------
        image: np.ndarray
        """
        return self._image

    @property
    def origin(self):
        # type: () -> Tuple[float, float]
        """
        Image Origin in Radians (phi, theta) a.k.a. (x,y)

        Returns
        -------
        origin: Tuple[float, float]
        """
        raise NotImplementedError()

    @property
    def aov(self):
        # type: () -> Tuple[float, float]
        """
        Image Angle of View in Radians (phi, theta) a.k.a. (x,y)

        Returns
        -------
        origin: Tuple[float, float]
        """
        raise NotImplementedError()

    def position_2d(self, coordinates):
        # type: (Tuple[float, float]) -> Tuple[float, float]
        """
        Return 2D position in Spherical Coordinates

        Parameters
        ----------
        coordinates: Tuple[float, float]

        Returns
        -------
        position_2d: Tuple[float, float]
        """
        phi_0, theta_0 = self.origin
        phi_1, theta_1 = self.aov
        x, y = coordinates

        return phi_0 + (x*2-1) * phi_1, theta_0 + (y*2-1) * theta_1

    def __repr__(self):
        return "{}{}".format(self.__class__.__name__, self.image.shape)


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

        self._processor_scheduler = Scheduler(self._processor, name="CameraThread")
        self._processor_scheduler.start()

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
        image: AbstractImage
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
