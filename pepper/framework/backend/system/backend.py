from pepper.framework.di_container import singleton
from pepper.framework.event.api import EventBusContainer
from pepper.framework.sensor.api import SensorContainer
from pepper.framework.abstract.backend import AbstractBackend
from pepper.framework.backend.container import BackendContainer
from pepper.framework.backend.system import SystemCamera, SystemMicrophone, SystemTextToSpeech,\
    SystemMotion, SystemLed, SystemTablet
from pepper import config, logger, CameraResolution

class SystemBackendContainer(BackendContainer, SensorContainer, EventBusContainer):
    logger.info("Initialized SystemBackendContainer")

    @property
    @singleton
    def backend(self):
        return SystemBackend(self.translator, self.event_bus)


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

    def __init__(self, translator_factory, event_bus,
                 camera_resolution=config.CAMERA_RESOLUTION,
                 camera_rate=config.CAMERA_FRAME_RATE,
                 microphone_channels=config.MICROPHONE_CHANNELS,
                 microphone_rate=config.MICROPHONE_SAMPLE_RATE,
                 language=config.APPLICATION_LANGUAGE):
        # type: (CameraResolution, int, int, int, str) -> None
        translator = translator_factory(config.INTERNAL_LANGUAGE[:2], language[:2])
        super(SystemBackend, self).__init__(SystemCamera(camera_resolution, camera_rate),
                                            SystemMicrophone(microphone_rate, microphone_channels, event_bus),
                                            SystemTextToSpeech(translator, language), SystemMotion(), SystemLed(), SystemTablet())
