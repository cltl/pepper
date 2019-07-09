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

    RESOLUTION_CODE = {
        CameraResolution.NATIVE:    2,
        CameraResolution.QQQQVGA:   8,
        CameraResolution.QQQVGA:    7,
        CameraResolution.QQVGA:     0,
        CameraResolution.QVGA:      1,
        CameraResolution.VGA:       2,
        CameraResolution.VGA4:      3,
    }

    COLOR_SPACE = {
        'kYuv': 0, 'kyUv': 1, 'kyuV': 2,
        'Rgb':  3, 'rGb':  4, 'rgB': 5,
        'Hsy':  6, 'hSy':  7, 'hsY': 8,

        'YUV422': 9,  # (Native Color)

        'YUV': 10, 'RGB': 11, 'HSY': 12,
        'BGR': 13, 'YYCbCr': 14,
        'H2RGB': 15, 'HSMixed': 16,

        'Depth': 17,        # uint16    - corrected distance from image plan (mm)
        'XYZ': 19,          # 3float32  - voxel xyz
        'Distance': 21,     # uint16    - distance from camera (mm)
        'RawDepth': 23,     # uint16    - distance from image plan (mm)
    }

    SERVICE_VIDEO = "ALVideoDevice"
    SERVICE_MOTION = "ALMotion"

    def __init__(self, session, resolution, rate, callbacks=[], index=NAOqiCameraIndex.TOP):
        super(NAOqiCamera, self).__init__(resolution, rate, callbacks)

        # Get random camera id, to prevent name collision
        self._id = str(getrandbits(128))

        self._color_space = 9  # YUV442
        self._color_space_3D = 17  # Distance from Camera in mm

        self._resolution = resolution
        self._resolution_3D = resolution

        self._rate = rate
        self._index = index

        # Connect to Camera Service and Subscribe with Settings
        self._service = session.service(NAOqiCamera.SERVICE_VIDEO)

        self._client = self._service.subscribeCameras(
            str(getrandbits(128)),  # Random Client ID's to prevent name collision
            [int(NAOqiCameraIndex.TOP), int(NAOqiCameraIndex.DEPTH)],
            [NAOqiCamera.RESOLUTION_CODE[resolution], NAOqiCamera.RESOLUTION_CODE[self._resolution_3D]],
            [self._color_space, self._color_space_3D],
            rate
        )

        # Access Head Motion for Image Coordinates
        self._motion = session.service(NAOqiCamera.SERVICE_MOTION)

        # Run image acquisition in Thread
        self._thread = Thread(target=self._run)
        self._thread.setDaemon(True)
        self._thread.start()

        self._log.debug("Booted")

    def _run(self):
        while True:
            if self._running:

                t0 = time()

                image_rgb = None
                image_3D = None
                image_bounds = None

                # Get Yaw and Pitch from Head Sensors
                yaw, pitch = self._motion.getAngles("HeadYaw", False)[0], self._motion.getAngles("HeadPitch", False)[0]

                # Get Image from Robot
                for image in self._service.getImagesRemote(self._client):
                    width, height, layers, color_space, seconds, milliseconds, data, camera, \
                    angle_left, angle_top, angle_right, angle_bottom = image

                    if camera == NAOqiCameraIndex.DEPTH:
                        image_3D = np.frombuffer(data, np.uint16).reshape(height, width).astype(np.float32) / 1000
                    else:
                        image_rgb = self._yuv2rgb(width, height, data)
                        image_bounds = Bounds(
                            angle_right - yaw,
                            angle_bottom + pitch + np.pi/2,
                            angle_left - yaw,
                            angle_top + pitch + np.pi/2
                        )

                if image_rgb is not None and image_bounds is not None:
                    self.on_image(NAOqiImage(image_rgb, image_bounds, image_3D))

                # Maintain frame rate
                sleep(max(1.0E-4, 1.0 / self.rate - (time() - t0)))

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