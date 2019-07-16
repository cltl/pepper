from threading import Thread, Lock
from Queue import Empty
from time import sleep
import numpy as np


class Scheduler(Thread):
    """Runs Task Continuously with certain interval"""

    def __init__(self, target, interval=1E-1, name=None, args=(), kwargs={}):
        Thread.__init__(self, name=name)
        self._target = target
        self._interval = interval
        self._args = args
        self._kwargs = kwargs
        self._running = False

        self.daemon = True

    def run(self):
        self._running = True
        while self._running:
            self._target(*self._args, **self._kwargs)
            sleep(self._interval)

    def join(self, timeout=None):
        self._running = False
        Thread.join(self, timeout)


class Mailbox(object):

    EPSILON = 1E-1

    def __init__(self):
        """Create Mailbox Object"""

        self._mutex = Lock()
        self._mail = None

    def put(self, mail):
        """
        Put new Mail in Mailbox

        Parameters
        ----------
        mail: Any
        """
        self._mail = mail

    def get(self, block=True):
        """
        Get Mail from Mailbox

        Parameters
        ----------
        block: bool
            If True: Wait for Mail until it arrives in Mailbox
            If False: Return Empty Exception when Mailbox is Empty

        Returns
        -------
        mail: Any
        """
        with self._mutex:
            if block:
                while self._mail is None:
                    sleep(Mailbox.EPSILON)
                return self._get()

            else:
                if self._mail is None:
                    raise Empty
                return self._get()

    def _get(self):
        """
        Get Mail & Empty Mailbox

        Returns
        -------
        mail: Any
        """
        mail = self._mail
        self._mail = None
        return mail


class Bounds(object):
    def __init__(self, x0, y0, x1, y1):
        """
        Parameters
        ----------
        x0: float
        y0: float
        x1: float
        y1: float
        """

        if x0 > x1 or y0 > y1:
            raise ValueError("Rectangle Error: Point (x1,y1) must be bigger than point (x0, y0)")

        self._x0 = x0
        self._y0 = y0
        self._x1 = x1
        self._y1 = y1

    @property
    def x0(self):
        """
        Returns
        -------
        x0: float
        """
        return self._x0

    @property
    def y0(self):
        """
        Returns
        -------
        y0: float
        """
        return self._y0

    @property
    def x1(self):
        """
        Returns
        -------
        x1: float
        """
        return self._x1

    @property
    def y1(self):
        """
        Returns
        -------
        y1: float
        """
        return self._y1

    @property
    def width(self):
        """
        Returns
        -------
        width: float
        """
        return self.x1 - self.x0

    @property
    def height(self):
        """
        Returns
        -------
        height: float
        """
        return self.y1 - self.y0

    @property
    def center(self):
        """
        Returns
        -------
        center: tuple
        """
        return (self.x0 + self.width / 2, self.y0 + self.height / 2)

    @property
    def area(self):
        """
        Returns
        -------
        area: float
        """
        return self.width * self.height

    def intersection(self, bounds):
        """
        Parameters
        ----------
        bounds: Bounds

        Returns
        -------
        intersection: Bounds or None
        """

        x0 = max(self.x0, bounds.x0)
        y0 = max(self.y0, bounds.y0)
        x1 = min(self.x1, bounds.x1)
        y1 = min(self.y1, bounds.y1)

        return None if x0 >= x1 or y0 >= y1 else Bounds(x0, y0, x1, y1)

    def overlap(self, other):
        """
        Calculate Overlap Factor

        Parameters
        ----------
        other: Bounds

        Returns
        -------
        overlap: float
        """

        intersection = self.intersection(other)

        if intersection:
            return min(intersection.area / self.area, self.area / intersection.area)
        else:
            return 0.0

    def is_subset_of(self, other):
        """
        Parameters
        ----------
        other: Bounds

        Returns
        -------
        is_subset_of: bool
            Whether 'other' Bounds is subset of 'this' Bounds
        """
        return self.x0 >= other.x0 and self.y0 >= other.y0 and self.x1 <= other.x1 and self.y1 <= other.y1

    def is_superset_of(self, other):
        """
        Parameters
        ----------
        other: Bounds

        Returns
        -------
        is_superset_of: bool
            Whether 'other' Bounds is superset of 'this' Bounds
        """
        return self.x0 <= other.x0 and self.y0 <= other.y0 and self.x1 >= other.x1 and self.y1 >= other.y1

    def contains(self, point):
        """
        Parameters
        ----------
        point: Tuple[float, float]

        Returns
        -------
        is_in: bool
            Whether Point lies in Bounds
        """
        x, y = point
        return self.x0 < x < self.x1 and self.y0 < y < self.y1

    def equals(self, other):
        """
        Parameters
        ----------
        other: Bounds

        Returns
        -------
        equals: bool
         Whether 'other' bounds equals 'this' bounds
        """
        return self.x0 == other.x0 and self.y0 == other.y0 and self.x1 == other.x1 and self.y1 == other.y1

    def scaled(self, x_scale, y_scale):
        """
        Return Scaled Bounds Object

        Parameters
        ----------
        x_scale: float
        y_scale: float

        Returns
        -------
        bounds: Bounds
            Scaled Bounds object
        """
        return Bounds(self.x0 * x_scale, self.y0 * y_scale, self.x1 * x_scale, self.y1 * y_scale)

    def to_list(self):
        return [self.x0, self.y0, self.x1, self.y1]

    def __repr__(self):
        return "Bounds[({:3f}, {:3f}), ({:3f}, {:3f})]".format(self.x0, self.y0, self.x1, self.y1)


def spherical2cartesian(phi, theta, depth):
    x = depth * np.sin(theta) * np.cos(phi)
    z = depth * np.sin(theta) * np.sin(phi)
    y = depth * np.cos(theta)

    return x, y, z