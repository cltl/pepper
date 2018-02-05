from enum import Enum, IntEnum
import numpy as np
import random


class Camera(object):
    def get(self):
        """
        Get Image

        Returns
        -------
        image: np.ndarray
        """
        raise NotImplementedError()


class CameraID(IntEnum):
    TOP = 0
    BOTTOM = 1
    DEPTH = 2


class CameraResolution(IntEnum):
    """
    Supported Pepper Camera Resolutions

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
    Supported Pepper Color Spaces

    KEY = (<ID>, (<channels>, <dtype>)
    """

    LUMINANCE = (0, (1, np.uint8))
    YUV = (10, (3, np.uint8))
    RGB = (11, (3, np.uint8))
    DEPTH = (17, (1, np.uint16))


class PepperCamera(Camera):
    def __init__(self, session, camera = CameraID.TOP, resolution = CameraResolution.VGA_160x120,
                 colorspace = CameraColorSpace.RGB, framerate = 30):

        self._session = session
        self._camera = camera
        self._resolution = resolution
        self._colorspace, (self._channels, self._dtype) = colorspace.value
        self._framerate = framerate

        self._id = str(random.getrandbits(128))

        self._service = self.session.service("ALVideoDevice")
        self._client = self.service.subscribeCamera(self.id,
                                                    int(self.camera),
                                                    int(self.resolution),
                                                    int(self.colorspace),
                                                    int(self.framerate))

    @property
    def session(self):
        return self._session

    @property
    def service(self):
        return self._service

    @property
    def client(self):
        return self._client

    @property
    def id(self):
        return self._id

    @property
    def camera(self):
        return self._camera

    @property
    def resolution(self):
        return self._resolution

    @property
    def colorspace(self):
        return self._colorspace

    @property
    def framerate(self):
        return self._framerate

    @property
    def channels(self):
        return self._channels

    @property
    def dtype(self):
        return self._dtype

    def get(self):
        result = self.service.getImageRemote(self.client)

        if result:
            width, height, layers, color_space, seconds, milliseconds, data, camera, \
            angle_left, angle_top, angle_right, angle_bottom = result
            return np.frombuffer(data, self.dtype).reshape(height, width, self.channels)

        else:
            self.service.unsubscribe(self.id)
            raise RuntimeError("No Result from ImageRemote")

