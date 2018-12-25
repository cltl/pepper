from pepper.framework import AbstractMicrophone

from webrtcvad import Vad
import numpy as np

from Queue import Queue

from typing import Iterable


class Utterance(object):
    def __init__(self):
        """Create Utterance Object"""
        self._queue = Queue()
        self._frames = []

    @property
    def frames(self):
        # type: () -> Iterable[np.ndarray]
        """
        Get Utterance Frames

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
        Get Utterance Audio (Concatenated Frames)

        Returns
        -------
        audio: np.ndarray
        """

        return np.concatenate([frame for frame in self.frames])

    def add_frame(self, frame):
        # type: (np.ndarray) -> None
        """
        Add Utterance Frame (done by VAD)

        Parameters
        ----------
        frame: np.ndarray
        """

        self._queue.put(frame)

    def __iter__(self):
        # type: () -> Iterable[np.ndarray]
        return self.frames


class VAD(object):

    AUDIO_FRAME_MS = 10
    BUFFER_SIZE = 100

    AUDIO_TYPE = np.int16
    AUDIO_TYPE_BYTES = 2

    VOICE_THRESHOLD = 0.6
    VOICE_WINDOW = 50

    MODE = 3

    def __init__(self, microphone):
        # type: (AbstractMicrophone) -> VAD
        """
        Perform Voice Activity Detection on Microphone Input
        
        Parameters
        ----------
        microphone: AbstractMicrophone
        """

        self._microphone = microphone

        self._vad = Vad(VAD.MODE)

        # Voice Activity Detection Frame Size, Atomic VAD Unit
        self._frame_size = VAD.AUDIO_FRAME_MS * self.microphone.rate // 1000
        self._frame_size_bytes = self._frame_size * VAD.AUDIO_TYPE_BYTES

        self._audio_buffer = np.zeros((VAD.BUFFER_SIZE, self._frame_size), VAD.AUDIO_TYPE)
        self._voice_buffer = np.zeros(VAD.BUFFER_SIZE, np.bool)
        self._buffer_index = 0

        self._utterance = None
        self._utterance_queue = Queue()

        self._frame_buffer = bytearray()

        self._activation = 0

        self.microphone.callbacks += [self._on_audio]

    @property
    def microphone(self):
        """
        VAD Microphone
        
        Returns
        -------
        microphone: AbstractMicrophone
        """
        return self._microphone

    @property
    def activation(self):
        """
        VAD Activation
        
        Returns
        -------
        activation: float
        """
        return self._activation

    @property
    def utterances(self):
        # type: () -> Iterable[Utterance]
        """
        Get Utterances from Microphone Stream

        Yields
        -------
        voices: Iterable of Voice
        """
        while True:
            yield self._utterance_queue.get()

    def _on_audio(self, audio):
        # type: (np.ndarray) -> None

        # Work through Microphone Stream Frame by Frame
        self._frame_buffer.extend(audio.tobytes())
        while len(self._frame_buffer) >= self._frame_size_bytes:
            self._on_frame(np.frombuffer(self._frame_buffer[:self._frame_size_bytes], VAD.AUDIO_TYPE))
            del self._frame_buffer[:self._frame_size_bytes]

    def _on_frame(self, frame):
        self._activation = self._calculate_activation(frame)

        if not self._utterance:
            if self.activation > VAD.VOICE_THRESHOLD:

                # Create New Utterance Object
                self._utterance = Utterance()

                # Add Buffer Contents to Utterance
                self._utterance.add_frame(self._audio_buffer[self._buffer_index:].ravel())
                self._utterance.add_frame(self._audio_buffer[:self._buffer_index].ravel())

                # Add Utterance to Utterance Queue
                self._utterance_queue.put(self._utterance)
        else:
            # If Utterance Ongoing: Add Frame to Utterance Object
            if self.activation > VAD.VOICE_THRESHOLD:
                self._utterance.add_frame(frame)

            # Else: Terminate Utterance
            else:
                self._utterance.add_frame(None)
                self._utterance = None

    def _calculate_activation(self, frame):
        # Update Buffers
        self._audio_buffer[self._buffer_index] = frame
        self._voice_buffer[self._buffer_index] = self._vad.is_speech(frame.tobytes(), self.microphone.rate, len(frame))
        self._buffer_index = (self._buffer_index + 1) % VAD.BUFFER_SIZE

        # Calculate Activation
        voice_window = np.arange(self._buffer_index - VAD.VOICE_WINDOW, self._buffer_index) % VAD.BUFFER_SIZE
        return np.mean(self._voice_buffer[voice_window])

    def __iter__(self):
        return self.utterances
