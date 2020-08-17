from pepper.framework.di_container import DIContainer


from asr import AbstractASR, AbstractTranslator, UtteranceHypothesis
from location import Location
from face import Face
from obj import Object
from vad import Voice


class SensorContainer(DIContainer):
    def asr(self, language=None):
        raise ValueError("ASR not configured")

    @property
    def vad(self):
        raise ValueError("VAD not configured")

    # TODO use for all translators
    def translator(self, source_language, target_language):
        raise ValueError("AbstractTranslator not configured")

    @property
    def face_detector(self):
        raise ValueError("FaceDetector not configured")

    def object_detector(self, target):
        raise ValueError("ObjectDetector not configured")


class FaceDetector(object):
    def represent(self, image):
        """
        Represent Face in Image as 128-dimensional vector

        Parameters
        ----------
        image: np.ndarray
            Image (possibly containing a human face)

        Returns
        -------
        result: list of (np.ndarray, Bounds)
            List of (representation, bounds)
        """
        raise NotImplementedError()


class ObjectDetector(object):
    def classify(self, image):
        # type: (AbstractImage) -> List[Object]
        """
        Classify Objects in Image

        Parameters
        ----------
        image: AbstractImage
            Image (Containing Objects)

        Returns
        -------
        objects: List[Object]
            Classified Objects
        """
        raise NotImplementedError()


class VAD(object):
    @property
    def voices(self):
        # type: () -> Iterable[Voice]
        """
        Get Voices from Microphone Stream

        Yields
        -------
        voices: Iterable[Voice]
        """
        raise NotImplementedError()