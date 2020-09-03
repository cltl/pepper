from Queue import Queue
from typing import Iterable

import numpy as np

from .asr import AbstractASR, AbstractTranslator, UtteranceHypothesis
from .location import Location
from .obj import Object
from pepper.framework.di_container import DIContainer
from pepper.framework.util import Bounds


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

    FEATURE_DIM = 128

    def represent(self, image):
        # type: (np.ndarray) -> Iterable[(np.ndarray, Bounds)]
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


class Voice(object):
    """Voice Object (for Voice Activity Detection: VAD)"""

    def __init__(self):
        # type: () -> None
        self._queue = Queue()
        self._frames = []

    @property
    def frames(self):
        # type: () -> Iterable[np.ndarray]
        """
        Get Voice Frames (chunks of audio)

        Yields
        -------
        frames: Iterable of np.ndarray
        """

        if self._frames:
            for frame in self._frames:
                yield frame
        else:
            while True:
                frame = self._queue.get()
                if frame is None:
                    break
                self._frames.append(frame)
                yield frame

    @property
    def audio(self):
        # type: () -> np.ndarray
        """
        Get Voice Audio (Concatenated Frames)

        Returns
        -------
        audio: np.ndarray
        """

        frames_ = [frame for frame in self.frames]
        return np.concatenate(frames_)

    def add_frame(self, frame):
        # type: (np.ndarray) -> None
        """
        Add Voice Frame (done by VAD)

        Parameters
        ----------
        frame: np.ndarray
        """

        self._queue.put(frame)

    def __iter__(self):
        # type: () -> Iterable[np.ndarray]
        return self.frames


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