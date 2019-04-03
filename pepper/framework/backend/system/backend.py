from pepper.framework.abstract import AbstractBackend
from pepper.framework.backend.system import SystemCamera, SystemMicrophone, SystemTextToSpeech, SystemLed
from pepper import config


class SystemBackend(AbstractBackend):
    """
    Initialize System Backend

    Parameters
    ----------
    camera_resolution: CameraResolution
        System Camera Resolution
    camera_rate: int
        System Camera Rate
    microphone_channels: int
        Number of System Microphone Channels
    microphone_rate: int
        System Microphone Bit Rate
    language: str
        System Language
    """

    def __init__(self,
                 camera_resolution=config.CAMERA_RESOLUTION,
                 camera_rate=config.CAMERA_FRAME_RATE,
                 microphone_channels=config.MICROPHONE_CHANNELS,
                 microphone_rate=config.MICROPHONE_SAMPLE_RATE,
                 language=config.APPLICATION_LANGUAGE):
        super(SystemBackend, self).__init__(SystemCamera(camera_resolution, camera_rate),
                                            SystemMicrophone(microphone_rate, microphone_channels),
                                            SystemTextToSpeech(language), SystemLed)
