from pepper.framework import AbstractComponent, AbstractApplication
from pepper.sensor import VAD, SynchronousGoogleASR, StreamedGoogleASR, ASRHypothesis
from pepper.framework.util import Scheduler
from pepper import config

import numpy as np

from Queue import Queue
from typing import *


class SpeechRecognitionComponent(AbstractComponent):
    @property
    def asr(self):
        """
        Returns
        -------
        asr: pepper.sensor.asr.SynchronousGoogleASR
        """
        raise NotImplementedError()

    @property
    def vad(self):
        """
        Returns
        -------
        vad: pepper.sensor.vad.VAD
        """
        raise NotImplementedError()

    def on_transcript(self, hypotheses, audio):
        """
        On Transcript Event. Called every time an utterance was understood by Automatic Speech Recognition.

        Parameters
        ----------
        hypotheses: list of ASRHypothesis
            Hypotheses about the corresponding utterance
        audio: numpy.ndarray
            Utterance audio
        """
        pass


class SynchronousSpeechRecognitionComponent(SpeechRecognitionComponent):
    def __init__(self, backend):
        """
        Construct Speech Recognition Component

        Parameters
        ----------
        backend: Backend
        """
        super(SynchronousSpeechRecognitionComponent, self).__init__(backend)

        self.on_transcript_callbacks = []
        self._asr = SynchronousGoogleASR(config.APPLICATION_LANGUAGE, self.backend.microphone.rate)

        def on_utterance(audio):
            hypotheses = self.asr.transcribe(audio)
            if hypotheses:

                # Call on_transcript Event Function
                self.on_transcript(hypotheses, audio)

                # Call Callback Functions
                for callback in self.on_transcript_callbacks:
                    callback(hypotheses, audio)

        self._vad = VAD(self.backend.microphone, [on_utterance])

    @property
    def asr(self):
        """
        Returns
        -------
        asr: pepper.sensor.asr.SynchronousGoogleASR
        """
        return self._asr

    @property
    def vad(self):
        """
        Returns
        -------
        vad: pepper.sensor.vad.VAD
        """
        return self._vad

    def on_transcript(self, hypotheses, audio):
        """
        On Transcript Event. Called every time an utterance was understood by Automatic Speech Recognition.

        Parameters
        ----------
        hypotheses: list of ASRHypothesis
            Hypotheses about the corresponding utterance
        audio: numpy.ndarray
            Utterance audio
        """
        pass


class StreamingSpeechRecognitionComponent(SpeechRecognitionComponent):
    def __init__(self, backend):
        """
        Construct Speech Recognition Component

        Parameters
        ----------
        backend: Backend
        """
        super(StreamingSpeechRecognitionComponent, self).__init__(backend)

        self.on_transcript_callbacks = []
        self._asr = StreamedGoogleASR(config.APPLICATION_LANGUAGE, self.backend.microphone.rate)

        frame_queue = Queue()
        self._vad = VAD(self.backend.microphone, stream_callbacks=[
            lambda audio, speech: frame_queue.put((audio, speech))])

        # TODO: Implement nicely
        self._speech_audio = []

        def frame_generator():
            speech = True
            self._speech_audio = []
            while speech:
                audio, speech = frame_queue.get()
                if speech: self._speech_audio.append(audio)
                yield audio

        def worker():
            audio, speech = frame_queue.get()

            if speech:
                utterance = frame_generator()

                hypotheses = self.asr.transcribe(utterance)

                if hypotheses:
                    # Combine Speech Audio Samples in one Array
                    speech_audio = np.concatenate(self._speech_audio)

                    # Call on_transcript Event Function
                    self.on_transcript(hypotheses, speech_audio)

                    # Call Callback Functions
                    for callback in self.on_transcript_callbacks:
                        callback(hypotheses, speech_audio)

        schedule = Scheduler(worker, name="StreamingSpeechRecognitionComponentThread")
        schedule.start()

    @property
    def asr(self):
        """
        Returns
        -------
        asr: pepper.sensor.asr.SynchronousGoogleASR
        """
        return self._asr

    @property
    def vad(self):
        """
        Returns
        -------
        vad: pepper.sensor.vad.VAD
        """
        return self._vad

    def on_transcript(self, hypotheses, audio):
        # type: (List[ASRHypothesis], np.ndarray) -> NoReturn
        """
        On Transcript Event. Called every time an utterance was understood by Automatic Speech Recognition.

        Parameters
        ----------
        hypotheses: List[ASRHypothesis]
            Hypotheses about the corresponding utterance
        audio: numpy.ndarray
            Utterance audio
        """
        pass
