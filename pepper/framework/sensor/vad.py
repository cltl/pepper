from Queue import Queue

import numpy as np
import webrtcvad
from typing import Iterable

from pepper.framework.abstract import AbstractMicrophone
from pepper.framework.abstract.microphone import TOPIC as MIC_TOPIC
from pepper.framework.event.api import EventBus, Event
from pepper.framework.resource.api import ResourceManager


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


# Don't import VAD for now until Voice is moved to API
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

    def __init__(self, microphone, event_bus, resource_manager, vad=None):
        # type: (AbstractMicrophone, EventBus, ResourceManager, object) -> None

        self._resource_manager = resource_manager
        self._microphone = microphone
        # TODO
        self._mic_lock = None
        self._vad = webrtcvad.Vad(WebRtcVAD.MODE) if not vad else vad

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
        # type: (Event) -> None
        """
        (Microphone Callback) Add Audio to VAD

        Parameters
        ----------
        event: Event
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

        if not self._mic_lock:
            self._mic_lock = self._resource_manager.get_read_lock(MIC_TOPIC)

        if not self._mic_lock.locked and not self._mic_lock.acquire(blocking=False):
            # Don't listen if the lock cannot be obtained
            return

        if not self._voice:
            # Only release the lock if there is no voice activity
            if self._mic_lock.interrupted:
                self._mic_lock.release()
                return

            if self._activation > WebRtcVAD.VOICE_THRESHOLD:
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
