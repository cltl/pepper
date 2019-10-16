from threading import Thread, Lock
from Queue import Empty
from time import sleep
import json
import numpy as np

from typing import Optional, List, Dict


class Scheduler(Thread):
    """
    Runs Threaded Task Continuously with certain interval

    This is useful for long running Real-Time tasks:
        When there are many of these tasks, they start to conflict with each other.
        By specifying an interval in which the CPU on this thread is told to sleep,
        breathing room is realized for the other threads to execute their commands.

    Parameters
    ----------
    target: Callable
        Function to Run
    interval: float
        Interval between function calls
    name: str or None
        Name of Thread (for identification in debug mode)
    args: tuple
        Target Arguments
    kwargs: dict
        Target Keyword Arguments
    """

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
    """
    Mailbox Object: Single-Item Queue with Override on 'put'
    """

    EPSILON = 1E-1

    def __init__(self):
        self._mutex = Lock()
        self._mail = None

    def put(self, mail):
        """
        Put new Mail in Mailbox, overriding any mail that might be there already

        Parameters
        ----------
        mail: Any
        """
        self._mail = mail

    def get(self, block=True):
        """
        Get latest Mail from Mailbox

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
    """
    Rectangle Bounds Object

    Parameters
    ----------
    x0: float
    y0: float
    x1: float
    y1: float
    """

    def __init__(self, x0, y0, x1, y1):
        # type: (float, float, float, float) -> None

        if x0 > x1 or y0 > y1:
            raise RuntimeWarning("Rectangle Error: Point (x1,y1) should be bigger than point (x0, y0)")

        self._x0 = x0
        self._y0 = y0
        self._x1 = x1
        self._y1 = y1

    @classmethod
    def from_json(cls, data):
        # type: (dict) -> Bounds
        """
        Create Bounds Object from Dictionary

        Parameters
        ----------
        data: dict
            Dictionary containing x0, y0, x1, y1 keys

        Returns
        -------
        bounds: Bounds
        """
        return cls(data["x0"], data["y0"], data["x1"], data["y1"])

    @property
    def x0(self):
        # type: () -> float
        """
        X0

        Returns
        -------
        x0: float
        """
        return self._x0

    @property
    def y0(self):
        # type: () -> float
        """
        Y0

        Returns
        -------
        y0: float
        """
        return self._y0

    @property
    def x1(self):
        # type: () -> float
        """
        X1

        Returns
        -------
        x1: float
        """
        return self._x1

    @property
    def y1(self):
        # type: () -> float
        """
        Y1

        Returns
        -------
        y1: float
        """
        return self._y1

    @property
    def width(self):
        # type: () -> float
        """
        Bounds Width

        Returns
        -------
        width: float
        """
        return self.x1 - self.x0

    @property
    def height(self):
        # type: () -> float
        """
        Bounds Height

        Returns
        -------
        height: float
        """
        return self.y1 - self.y0

    @property
    def center(self):
        # type: () -> (float, float)
        """
        Bounds Center

        Returns
        -------
        center: tuple
        """
        return (self.x0 + self.width / 2, self.y0 + self.height / 2)

    @property
    def area(self):
        # type: () -> float
        """
        Bounds Area

        Returns
        -------
        area: float
        """
        return self.width * self.height

    def intersection(self, bounds):
        # type: (Bounds) -> Optional[Bounds]
        """
        Bounds Intersection with another Bounds

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
        # type: (Bounds) -> float
        """
        Bounds Overlap Ratio

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
        # type: (Bounds) -> bool
        """
        Whether 'other' Bounds is subset of 'this' Bounds

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
        # type: (Bounds) -> float
        """
        Whether 'other' Bounds is superset of 'this' Bounds

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
        # type: ((float, float)) -> bool
        """
        Whether Point lies in Bounds

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
        # type: (Bounds) -> bool
        """
        Whether 'other' bounds equals 'this' bounds

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
        # type: (float, float) -> Bounds
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
        # type: () -> List[float]
        """
        Export Bounds as List

        Returns
        -------
        bounds: List[float]
        """
        return [self.x0, self.y0, self.x1, self.y1]

    def dict(self):
        # type: () -> Dict[str, float]
        """
        Export Bounds as Dict

        Returns
        -------
        dict: Dict[str, float]
        """
        return {
            "x0": self.x0,
            "y0": self.y0,
            "x1": self.x1,
            "y1": self.y1
        }

    @property
    def json(self):
        # type: () -> str
        """
        Export Bounds as JSON

        Returns
        -------
        json: str
        """
        return json.dumps(self.dict())

    def __repr__(self):
        return "Bounds[({:3f}, {:3f}), ({:3f}, {:3f})]".format(self.x0, self.y0, self.x1, self.y1)


def spherical2cartesian(phi, theta, depth):
    """
    Spherical Coordinates to Cartesian Coordinates

    Phi: Left to Right, Theta: Down to Up, Depth: Distance
    x: Left to Right, y: down to up, z: close to far

    Parameters
    ----------
    phi: float
    theta: float
    depth: float

    Returns
    -------
    x,y,z: float, float, float

    """
    x = depth * np.sin(theta) * np.cos(phi)
    y = depth * np.cos(theta)
    z = depth * np.sin(theta) * np.sin(phi)

    return x, y, z