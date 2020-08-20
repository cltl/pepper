from pepper.framework.abstract.camera import AbstractCamera, AbstractImage
from pepper.framework.util import Bounds
from pepper import NAOqiCameraIndex, CameraResolution

import qi

import numpy as np

from random import getrandbits
from threading import Thread
from time import time, sleep

from typing import List, Callable


class NAOqiImage(AbstractImage):
    """NAOqi Image (same as AbstractImage)"""
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
    event_bus: EventBus
        Event bus of the application
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

    # Only take non-blurry pictures
    HEAD_DELTA_THRESHOLD = 0.1

    def __init__(self, session, resolution, rate, event_bus, index=NAOqiCameraIndex.TOP):
        # type: (qi.Session, CameraResolution, int, event_bus, NAOqiCameraIndex) -> None
        super(NAOqiCamera, self).__init__(resolution, rate, event_bus)

        # Get random camera id, to prevent name collision
        self._id = str(getrandbits(128))

        self._color_space = self.COLOR_SPACE['YUV422']
        self._color_space_3D = self.COLOR_SPACE['Distance']

        self._resolution = resolution
        self._resolution_3D = resolution

        self._rate = rate
        self._index = index

        # Connect to Camera Service and Subscribe with Settings
        self._service = session.service(NAOqiCamera.SERVICE_VIDEO)

        # Access Head Motion for Image Coordinates
        self._motion = session.service(NAOqiCamera.SERVICE_MOTION)

        # Subscribe to Robot Cameras
        self._client = self._service.subscribeCameras(
            str(getrandbits(128)),  # Random Client ID's to prevent name collision
            [int(NAOqiCameraIndex.TOP), int(NAOqiCameraIndex.DEPTH)],
            [NAOqiCamera.RESOLUTION_CODE[resolution], NAOqiCamera.RESOLUTION_CODE[self._resolution_3D]],
            [self._color_space, self._color_space_3D],
            rate
        )

        # Run Image Acquisition in Thread
        self._thread = Thread(target=self._run, name="NAOqiCameraThread")
        self._thread.setDaemon(True)
        self._thread.start()

        # # Create High Rate Camera
        # self._client_high_rate = self._service.subscribeCamera(
        #     str(getrandbits(128)),
        #     int(NAOqiCameraIndex.TOP),
        #     NAOqiCamera.RESOLUTION_CODE[CameraResolution.QQQVGA],
        #     self._color_space,
        #     30
        # )

        # # Run High Rate Image Acquisition in Thread
        # self._thread_high_rate = Thread(target=self._run_high_rate, name="NAOqiHighRateCameraThread")
        # self._thread_high_rate.setDaemon(True)
        # self._thread_high_rate.start()

        self._log.debug("Booted")

    # def _run_high_rate(self):
    #     while True:
    #         image = self._service.getImageRemote(self._client_high_rate)

    def _run(self):
        while True:
            if self._running:

                t0 = time()

                # Initialize RGB, 3D and Image Bounds
                image_rgb, image_3D, bounds = None, None, None

                # Get Yaw and Pitch from Head Sensors
                # TODO: Make sure these are the Head Yaw and Pitch at image capture time!?
                yaw, pitch = self._motion.getAngles("HeadYaw", False)[0], self._motion.getAngles("HeadPitch", False)[0]

                # Get Image from Robot
                for image in self._service.getImagesRemote(self._client):

                    # Get Image Data
                    # TODO: RGB and Depth Images are not perfectly synced, can they?
                    width, height, _, _, _, _, data, camera, left, top, right, bottom = image

                    if camera == NAOqiCameraIndex.DEPTH:
                        # Get Depth Image and Convert from Millimeters to Meters
                        # TODO: Make sure Image Bounds are actually the same for RGB and Depth Camera!
                        image_3D = np.frombuffer(data, np.uint16).reshape(height, width).astype(np.float32) / 1000
                    else:
                        # Get Image Data and Convert from YUV422 to RGB
                        image_rgb = self._yuv2rgb(width, height, data)

                        # Calculate Image Bounds in Radians
                        # Apply Yaw and Pitch to Image Bounds
                        # Bring Theta from [-PI/2,+PI/2] to [0, PI] Space
                        phi_min, phi_max = right - yaw, left - yaw
                        theta_min, theta_max = bottom + pitch + np.pi/2, top + pitch + np.pi/2
                        bounds = Bounds(phi_min, theta_min, phi_max, theta_max)

                # Assert we have at least a RGB image and Bounds
                if image_rgb is not None and bounds is not None:

                    # Call AbstractCamera.on_image Callback
                    self.on_image(NAOqiImage(image_rgb, bounds, image_3D))

                # Maintain frame rate
                sleep(max(1.0E-4, 1.0 / self.rate - (time() - t0)))

    def _yuv2rgb(self, width, height, data):
        # type: (int, int, bytes) -> np.ndarray
        """
        Convert from YUV422 to RGB Color Space

        Parameters
        ----------
        width: int
            Image Width
        height: int
            Image Height
        data: bytes
            Image Data

        Returns
        -------
        image_rgb: np.ndarray
        """

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
