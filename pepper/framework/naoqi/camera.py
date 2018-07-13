from pepper.framework.abstract.camera import AbstractCamera
from pepper.framework.enumeration import NaoqiCameraIndex, CameraResolution

import numpy as np

from random import getrandbits
from threading import Thread
from time import sleep
import logging


class NaoqiCamera(AbstractCamera):

    SERVICE = "ALVideoDevice"
    COLOR_SPACE = 9 # YUV442

    RESOLUTION_CODE = {
        CameraResolution.QQQQVGA: 8,
        CameraResolution.QQQVGA: 7,
        CameraResolution.QQVGA: 0,
        CameraResolution. QVGA: 1,
        CameraResolution.VGA: 2,
        CameraResolution.VGA4: 3,
    }


    def __init__(self, session, resolution, rate, callbacks=[], index=NaoqiCameraIndex.TOP):
        super(NaoqiCamera, self).__init__(resolution, rate, callbacks)

        self._id = str(getrandbits(128))
        self._service = session.service(NaoqiCamera.SERVICE)
        self._client = self._service.subscribeCamera(
            self._id, int(index), NaoqiCamera.RESOLUTION_CODE[resolution], NaoqiCamera.COLOR_SPACE, rate)

        self._log = logging.getLogger(self.__class__.__name__)
        self._log.debug("Booted")

        self._thread = Thread(target=self._run)
        self._thread.setDaemon(True)
        self._thread.start()

    def _run(self):
        while True:
            if self._running:
                result = self._service.getImageRemote(self._client)

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

                    self.on_image(RGB.clip(0, 255).astype(np.uint8).reshape(Y, X, 3))
                else:
                    self._service.unsubscribe(self._id)
                    raise RuntimeWarning("{} could not fetch image".format(self.__class__.__name__))

                sleep(1. / self.rate)