from pepper.framework.abstract.camera import AbstractCamera, AbstractImage
from pepper.framework.util import Bounds
from pepper import NAOqiCameraIndex, CameraResolution

import numpy as np

from random import getrandbits
from threading import Thread
from time import time, sleep


class NAOqiImage(AbstractImage):
    pass


class NAOqiCamera(AbstractCamera):
    """
    NAOqi Camera

    Parameters
    ----------
    session: qi.Session
        NAOqi Application Session
    resolution: CameraResolution
        NAOqi Camera Resolution
    rate: int
        NAOqi Camera Rate
    callbacks: list of callable
        On Image Event Callbacks
    index: int
        Which NAOqi Camera to use
    """

    SERVICE = "ALVideoDevice"
    COLOR_SPACE_YUV = 9  # YUV442
    COLOR_SPACE_3D = 21  # Distance from Camera in mm

    RESOLUTION_CODE_3D = {
        'k720p': 5,
        'kQ720p': 9,
        'kQQ720p': 10,
        'kQQQ720p': 11,
        'kQQQQ720p': 12,
    }

    RESOLUTION_CODE = {
        CameraResolution.NATIVE: 2,
        CameraResolution.QQQQVGA: 8,
        CameraResolution.QQQVGA: 7,
        CameraResolution.QQVGA: 0,
        CameraResolution.QVGA: 1,
        CameraResolution.VGA: 2,
        CameraResolution.VGA4: 3,
    }

    def __init__(self, session, resolution, rate, callbacks=[], index=NAOqiCameraIndex.TOP):
        super(NAOqiCamera, self).__init__(resolution, rate, callbacks)

        # Get random camera id, to prevent name collision
        self._id = str(getrandbits(128))

        self._resolution = resolution
        self._rate = rate
        self._index = index

        # Connect to Camera Service and Subscribe with Settings
        self._service = session.service(NAOqiCamera.SERVICE)

        self._client = self._service.subscribeCameras(
            str(getrandbits(128)),  # Random Client ID's to prevent name collision
            [int(NAOqiCameraIndex.TOP), int(NAOqiCameraIndex.DEPTH)],
            [NAOqiCamera.RESOLUTION_CODE[resolution], 12],
            [NAOqiCamera.COLOR_SPACE_YUV, NAOqiCamera.COLOR_SPACE_3D],
            rate
        )

        # Access Head Motion for Image Coordinates
        self._motion = session.service("ALMotion")

        self._aov = tuple(abs(a) for a in self._service.getAngularPositionFromImagePosition(int(index), [1, 1]))

        # Run image acquisition in Thread
        self._thread = Thread(target=self._run)
        self._thread.setDaemon(True)
        self._thread.start()

        self._log.debug("Booted")

    def _run(self):
        while True:
            if self._running:

                t0 = time()

                # Get Yaw and Pitch from Head Sensors
                yaw, pitch = self._motion.getAngles("HeadYaw", False)[0], self._motion.getAngles("HeadPitch", False)[0]

                image_rgb = None
                image_3D = None
                image_bounds = None

                # Get Image from Robot
                for image in self._service.getImagesRemote(self._client):
                    width, height, layers, color_space, seconds, milliseconds, data, camera, \
                    angle_left, angle_top, angle_right, angle_bottom = image

                    if camera == NAOqiCameraIndex.DEPTH:
                        image_3D = np.frombuffer(data, np.uint16).reshape(height, width)
                    else:
                        image_rgb = self._yuv2rgb(width, height, data)
                        image_bounds = Bounds(angle_right + yaw,
                                              angle_bottom + pitch,
                                              angle_left + yaw,
                                              angle_top + pitch)

                self.on_image(NAOqiImage(image_rgb, image_bounds, image_3D))

                # Maintain frame rate
                sleep(max(0, 1. / self.rate - (time() - t0)))

    def _yuv2rgb(self, width, height, data):

        X2 = width // 2

        YUV442 = np.frombuffer(data, np.uint8).reshape(height, X2, 4)

        RGB = np.empty((height, X2, 2, 3), np.float32)
        RGB[:, :, 0, :] = YUV442[..., 0].reshape(height, X2, 1)
        RGB[:, :, 1, :] = YUV442[..., 2].reshape(height, X2, 1)

        Cr = (YUV442[..., 1].astype(np.float32) - 128.0).reshape(height, X2, 1)
        Cb = (YUV442[..., 3].astype(np.float32) - 128.0).reshape(height, X2, 1)

        RGB[..., 0] += np.float32(1.402) * Cb
        RGB[..., 1] += - np.float32(0.71414) * Cb - np.float32(0.34414) * Cr
        RGB[..., 2] += np.float32(1.772) * Cr

        return RGB.clip(0, 255).astype(np.uint8).reshape(height, width, 3)