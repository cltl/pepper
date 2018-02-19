import numpy as np
import cv2

from enum import Enum, IntEnum
import random


class Camera(object):
    """Abstract Camera Class"""

    def get(self):
        """
        Get Image as Numpy Array

        Returns
        -------
        image: np.ndarray
        """
        raise NotImplementedError()


class CameraTarget(IntEnum):
    """Target Camera for PepperCamera"""

    TOP = 0
    BOTTOM = 1
    DEPTH = 2


class CameraResolution(IntEnum):
    """
    Supported Resolutions for Pepper Camera

    KEY = (<ID>, (<width>, <height>))
    """

    VGA_40x30 = 8
    VGA_80x60 = 7
    VGA_160x120 = 0
    VGA_320x240 = 1
    VGA_640x480 = 2
    VGA_1280x960 = 3


class CameraColorSpace(Enum):
    """
    Supported Color Spaces for Pepper Camera

    KEY = (<ID>, (<channels>, <dtype>)
    """

    LUMINANCE = (0, (1, np.uint8))
    YUV = (10, (3, np.uint8))
    RGB = (11, (3, np.uint8))
    DEPTH = (17, (1, np.uint16))


class PepperCamera(Camera):
    def __init__(self, session, camera_target = CameraTarget.TOP, resolution = CameraResolution.VGA_160x120,
                 colorspace = CameraColorSpace.RGB, framerate = 30):
        """


        Parameters
        ----------
        session
        camera_target
        resolution
        colorspace
        framerate
        """
        self._session = session
        self._camera_target = camera_target
        self._resolution = resolution
        self._colorspace, (self._channels, self._dtype) = colorspace.value
        self._framerate = framerate

        self._id = str(random.getrandbits(128))

        self._service = self.session.service("ALVideoDevice")
        self._client = self.service.subscribeCamera(self.id,
                                                    int(self.camera_target),
                                                    int(self.resolution),
                                                    int(self.colorspace),
                                                    int(self.framerate))

    @property
    def session(self):
        """
        Returns
        -------
        session: qi.Session
        """
        return self._session

    @property
    def service(self):
        """
        Returns
        -------
        service
            ALVideoDevice Service
        """
        return self._service

    @property
    def client(self):
        """
        Returns
        -------
        client
            ALVideoDevice Client
        """
        return self._client

    @property
    def id(self):
        """
        Returns
        -------
        id: str
            Camera ID (random hash, to avoid conflicts)
        """
        return self._id

    @property
    def camera_target(self):
        """
        Returns
        -------
        camera_target: CameraTarget
            Camera Target
        """
        return self._camera_target

    @property
    def resolution(self):
        """
        Returns
        -------
        resolution: CameraResolution
            Camera Resolution
        """
        return self._resolution

    @property
    def colorspace(self):
        """
        Returns
        -------
        colorspace: CameraColorSpace
            Camera Color Space
        """
        return self._colorspace

    @property
    def framerate(self):
        """
        Returns
        -------
        framerate: int
            Camera Frame Rate
        """
        return self._framerate

    @property
    def channels(self):
        """
        Returns
        -------
        channels: int
            Number of Channels (e.g. 3 for RGB, 1 for Luminance)
        """
        return self._channels

    @property
    def dtype(self):
        """
        Returns
        -------
        dtype: np.dtype
            Data type of each element in image
        """
        return self._dtype

    def get(self):
        """
        Get Image as Numpy Array

        Returns
        -------
        image: np.ndarray
        """
        result = self.service.getImageRemote(self.client)

        if result:
            width, height, layers, color_space, seconds, milliseconds, data, camera, \
            angle_left, angle_top, angle_right, angle_bottom = result
            return np.frombuffer(data, self.dtype).reshape(height, width, self.channels)

        else:
            self.service.unsubscribe(self.id)
            raise RuntimeError("No Result from ImageRemote")


class SystemCamera(Camera):
    def __init__(self):
        self._capture = cv2.VideoCapture(0)

    def get(self):
        """
        Get Image as Numpy Array

        Returns
        -------
        image: np.ndarray
        """
        ret, frame = self._capture.read()
        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
