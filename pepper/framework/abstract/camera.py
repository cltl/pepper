from pepper.framework.util import Mailbox, Scheduler, Bounds, spherical2cartesian
from pepper import CameraResolution
from pepper import logger

import numpy as np

from collections import deque
from time import time

from typing import Tuple, List, Optional, Callable


class AbstractImage(object):

    def __init__(self, image, bounds, depth=None):
        # type: (np.ndarray, Bounds, Optional[np.ndarray]) -> None
        """
        Abstract Image Container

        Parameters
        ----------
        image: np.ndarray
        bounds: Bounds
        depth: np.ndarray
        """

        self._image = image
        self._bounds = bounds
        self._depth = np.ones((100, 100), np.float32) if depth is None else depth

        self._time = time()

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
    def depth(self):
        # type: () -> Optional[np.ndarray]
        return self._depth

    @property
    def bounds(self):
        # type: () -> Bounds
        return self._bounds

    def get_image(self, bounds):
        # type: (Bounds) -> np.ndarray
        x0 = int(bounds.x0 * self._image.shape[1])
        x1 = int(bounds.x1 * self._image.shape[1])
        y0 = int(bounds.y0 * self._image.shape[0])
        y1 = int(bounds.y1 * self._image.shape[0])

        return self._image[y0:y1, x0:x1]

    def get_depth(self, bounds):
        # type: (Bounds) -> Optional[np.ndarray]

        if self._depth is None:
            return None

        x0 = int(bounds.x0 * self._depth.shape[1])
        x1 = int(bounds.x1 * self._depth.shape[1])
        y0 = int(bounds.y0 * self._depth.shape[0])
        y1 = int(bounds.y1 * self._depth.shape[0])

        return self._depth[y0:y1, x0:x1]

    def get_direction(self, coordinates):
        # type: (Tuple[float, float]) -> Tuple[float, float]
        """
        Convert 2D Relative Coordinates to 2D position in Spherical Coordinates

        Parameters
        ----------
        coordinates: Tuple[float, float]

        Returns
        -------
        position_2D: Tuple[float, float]
        """
        return (self.bounds.x0 + coordinates[0] * self.bounds.width,
                self.bounds.y0 + coordinates[1] * self.bounds.height)

    @property
    def time(self):
        # type: () -> float
        return self._time

    def frustum(self, depth_min, depth_max):
        # type: (float, float) -> List[float]
        return [
            spherical2cartesian(self._bounds.x0, self._bounds.y0, depth_min),
            spherical2cartesian(self._bounds.x0, self._bounds.y1, depth_min),
            spherical2cartesian(self._bounds.x1, self._bounds.y1, depth_min),
            spherical2cartesian(self._bounds.x1, self._bounds.y0, depth_min),

            spherical2cartesian(self._bounds.x0, self._bounds.y0, depth_max),
            spherical2cartesian(self._bounds.x0, self._bounds.y1, depth_max),
            spherical2cartesian(self._bounds.x1, self._bounds.y1, depth_max),
            spherical2cartesian(self._bounds.x1, self._bounds.y0, depth_max),
        ]

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
        # type: (CameraResolution, int, List[Callable[[AbstractImage], None]]) -> None

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
        # type: () -> CameraResolution
        """
        Returns :class:`~pepper.config.CameraResolution`

        Returns
        -------
        resolution: CameraResolution
        """
        return self._resolution

    @property
    def width(self):
        # type: () -> int
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
        # type: () -> int
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
        # type: () -> int
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
        # type: () -> int
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
        # type: () -> float
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
        # type: () -> np.ndarray
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
        # type: () -> List[Callable[[AbstractImage], None]]
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
        # type: (List[Callable[[AbstractImage], None]]) -> None
        """
        Get/Set :func:`~AbstractCamera.on_image` Callbacks

        Parameters
        ----------
        value: list of callable
        """
        self._callbacks = value

    @property
    def running(self):
        # type: () -> bool
        """
        Returns whether Camera is Running

        Returns
        -------
        running: bool
        """
        return self._running

    def on_image(self, image):
        # type: (AbstractImage) -> None
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
