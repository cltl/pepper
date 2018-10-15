from pepper.framework.abstract import AbstractBackend
from pepper.framework.backend.system import SystemCamera, SystemMicrophone, SystemTextToSpeech
from pepper import config


class SystemBackend(AbstractBackend):
    def __init__(self,
                 camera_resolution=config.CAMERA_RESOLUTION,
                 camera_rate=config.CAMERA_FRAME_RATE,
                 microphone_channels=config.MICROPHONE_CHANNELS,
                 microphone_rate=config.MICROPHONE_SAMPLE_RATE,
                 language=config.LANGUAGE):
        """
        Initialize System Backend

        Parameters
        ----------
        camera_resolution: pepper.framework.abstract.camera.CameraResolution
        camera_rate: int
        microphone_channels: int
        microphone_rate: int
        language: str
        """

        super(SystemBackend, self).__init__(SystemCamera(camera_resolution, camera_rate),
                                            SystemMicrophone(microphone_rate, microphone_channels),
                                            SystemTextToSpeech(language))
