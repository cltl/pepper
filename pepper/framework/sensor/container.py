from .api import SensorContainer
from .asr import StreamedGoogleASR, GoogleTranslator
from .face import OpenFace
from .obj import ObjectDetectionClient
from .vad import WebRtcVAD
from pepper.framework.di_container import singleton
from pepper.framework.backend.container import BackendContainer
from pepper.framework.event.api import EventBusContainer
from pepper import logger


class DefaultSensorContainer(BackendContainer, SensorContainer, EventBusContainer):
    logger.info("Initialized DefaultSensorContainer")

    def asr(self, language=None):
        return StreamedGoogleASR() if language is None else StreamedGoogleASR(language)

    @property
    @singleton
    def vad(self):
        return WebRtcVAD(self.backend.microphone, self.event_bus)

    def translator(self, source_language, target_language):
        return GoogleTranslator(source_language, target_language)

    @property
    @singleton
    def face_detector(self):
        return OpenFace()

    def object_detector(self, target):
        return ObjectDetectionClient(target)

