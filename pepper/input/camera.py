import numpy as np
import cv2

from enum import Enum, IntEnum
import random

from numba import jit


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


class PepperCamera(Camera):
    def __init__(self, session, camera_target = CameraTarget.TOP,
                 resolution = CameraResolution.VGA_320x240, framerate = 10):
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
        self._framerate = framerate

        self._id = str(random.getrandbits(128))

        self._service = self.session.service("ALVideoDevice")
        self._client = self.service.subscribeCamera(self.id,
                                                    int(self.camera_target),
                                                    int(self.resolution),
                                                    9,  #YUV422,
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
    def framerate(self):
        """
        Returns
        -------
        framerate: int
            Camera Frame Rate
        """
        return self._framerate

    def get(self):
        """
        Get Image as Numpy Array

        Returns
        -------
        image: np.ndarray
        """

        result = self.service.getImageRemote(self.client)

        if result:
            X, Y, layers, color_space, seconds, milliseconds, data, camera, \
            angle_left, angle_top, angle_right, angle_bottom = result

            X2 = X // 2

            YUV442 = np.frombuffer(data, np.uint8).reshape(Y, X2, 4)

            RGB = np.empty((Y, X2, 2, 3), np.float32)
            RGB[:, :, 0, :] = YUV442[..., 0].reshape(Y, X2, 1)
            RGB[:, :, 1, :] = YUV442[..., 2].reshape(Y, X2, 1)

            Cr = (YUV442[..., 1].astype(np.float32) - 128.0).reshape(Y, X2, 1)
            Cb = (YUV442[..., 3].astype(np.float32) - 128.0).reshape(Y, X2, 1)

            RGB[..., 0] += np.float32(1.402) * Cb
            RGB[..., 1] += - np.float32(0.71414) * Cb - np.float32(0.34414) * Cr
            RGB[..., 2] += np.float32(1.772) * Cr

            return RGB.clip(0, 255).astype(np.uint8).reshape(Y, X, 3)

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
