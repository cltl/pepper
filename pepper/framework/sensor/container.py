from pepper import logger
from pepper.framework.backend.container import BackendContainer
from pepper.framework.di_container import singleton, singleton_for_kw
from pepper.framework.event.api import EventBusContainer
from pepper.framework.resource.api import ResourceContainer
from .api import SensorContainer
from .asr import StreamedGoogleASR, GoogleTranslator
from .face_detect import OpenFace
from .obj import ObjectDetectionClient
from .vad import WebRtcVAD


class DefaultSensorContainer(BackendContainer, SensorContainer, EventBusContainer, ResourceContainer):
    logger.info("Initialized DefaultSensorContainer")

    @singleton_for_kw(["language"])
    def asr(self, language=None):
        return StreamedGoogleASR() if language is None else StreamedGoogleASR(language)

    @property
    @singleton
    def vad(self):
        return WebRtcVAD(self.backend.microphone, self.event_bus, self.resource_manager)

    @singleton_for_kw(["source_language", "target_language"])
    def translator(self, source_language=None, target_language=None):
        return GoogleTranslator(source_language, target_language)

    @property
    @singleton
    def face_detector(self):
        return OpenFace()

    def object_detector(self, target):
        return ObjectDetectionClient(target)

