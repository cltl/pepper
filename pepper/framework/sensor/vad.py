from pepper.framework.abstract import AbstractMicrophone
from pepper.framework.abstract.microphone import TOPIC as MIC_TOPIC

from webrtcvad import Vad
import numpy as np

from Queue import Queue

from typing import Iterable


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

        return np.concatenate([frame for frame in self.frames])

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

# TODO Don't extend VAD for now to avoid circular dependency
class WebRtcVAD(object):
    """
    Perform Voice Activity Detection on Microphone Input

    Parameters
    ----------
    microphone: AbstractMicrophone
    """

    AUDIO_FRAME_MS = 10
    BUFFER_SIZE = 100

    AUDIO_TYPE = np.int16
    AUDIO_TYPE_BYTES = 2

    VOICE_THRESHOLD = 0.6
    VOICE_WINDOW = 50

    MODE = 3

    def __init__(self, microphone, event_bus):
        # type: (AbstractMicrophone, EventBus) -> None

        self._microphone = microphone
        self._vad = Vad(WebRtcVAD.MODE)

        # Voice Activity Detection Frame Size: VAD works in units of 'frames'
        self._frame_size = WebRtcVAD.AUDIO_FRAME_MS * self.microphone.rate // 1000
        self._frame_size_bytes = self._frame_size * WebRtcVAD.AUDIO_TYPE_BYTES

        # Audio & Voice Ring-Buffers
        self._audio_buffer = np.zeros((WebRtcVAD.BUFFER_SIZE, self._frame_size), WebRtcVAD.AUDIO_TYPE)
        self._voice_buffer = np.zeros(WebRtcVAD.BUFFER_SIZE, np.bool)
        self._buffer_index = 0

        self._voice = None
        self._voice_queue = Queue()

        self._frame_buffer = bytearray()

        self._activation = 0

        # Subscribe VAD to Microphone on_audio event
        event_bus.subscribe(MIC_TOPIC, self._on_audio)

    @property
    def microphone(self):
        # type: () -> AbstractMicrophone
        """
        VAD Microphone

        Returns
        -------
        microphone: AbstractMicrophone
        """
        return self._microphone

    @property
    def activation(self):
        # type: () -> float
        """
        VAD Activation

        Returns
        -------
        activation: float
        """
        return self._activation

    # TODO change the API to accept audio and return voices, i.e.
    # move _on_audio to the place that calls this (iterates this VAD)
    # Then we can simply Mock this class in itests
    @property
    def voices(self):
        # type: () -> Iterable[Voice]
        """
        Get Voices from Microphone Stream

        Yields
        -------
        voices: Iterable[Voice]
        """
        while True:
            yield self._voice_queue.get()

    def _on_audio(self, event):
        # type: (np.ndarray) -> None
        """
        (Microphone Callback) Add Audio to VAD

        Parameters
        ----------
        audio: Event
        """

        # Work through Microphone Stream Frame by Frame
        audio = event.payload
        self._frame_buffer.extend(audio.tobytes())
        while len(self._frame_buffer) >= self._frame_size_bytes:
            self._on_frame(np.frombuffer(self._frame_buffer[:self._frame_size_bytes], WebRtcVAD.AUDIO_TYPE))
            del self._frame_buffer[:self._frame_size_bytes]

    def _on_frame(self, frame):
        # type: (np.ndarray) -> None
        """
        Is-Speech/Is-Not-Speech Logic, called every frame

        Parameters
        ----------
        frame: np.ndarray
        """
        self._activation = self._calculate_activation(frame)

        if not self._voice:
            if self.activation > WebRtcVAD.VOICE_THRESHOLD:

                # Create New Utterance Object
                self._voice = Voice()

                # Add Buffer Contents to Utterance
                self._voice.add_frame(self._audio_buffer[self._buffer_index:].ravel())
                self._voice.add_frame(self._audio_buffer[:self._buffer_index].ravel())

                # Add Utterance to Utterance Queue
                self._voice_queue.put(self._voice)
        else:
            # If Utterance Ongoing: Add Frame to Utterance Object
            if self.activation > WebRtcVAD.VOICE_THRESHOLD:
                self._voice.add_frame(frame)

            # Else: Terminate Utterance
            else:
                self._voice.add_frame(None)
                self._voice = None

    def _calculate_activation(self, frame):
        # type: (np.ndarray) -> float
        """
        Calculate Voice Activation

        Parameters
        ----------
        frame: np.ndarray

        Returns
        -------
        activation: float
        """
        # Update Buffers
        self._audio_buffer[self._buffer_index] = frame
        self._voice_buffer[self._buffer_index] = self._vad.is_speech(frame.tobytes(), self.microphone.rate, len(frame))
        self._buffer_index = (self._buffer_index + 1) % WebRtcVAD.BUFFER_SIZE

        # Calculate Activation
        voice_window = np.arange(self._buffer_index - WebRtcVAD.VOICE_WINDOW, self._buffer_index) % WebRtcVAD.BUFFER_SIZE
        return float(np.mean(self._voice_buffer[voice_window]))

    def __iter__(self):
        # type: () -> Iterable[Voice]
        """
        Get Voices from Microphone Stream

        Yields
        -------
        voices: Iterable[Voice]
        """
        return self.voices
