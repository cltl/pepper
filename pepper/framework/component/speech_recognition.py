from pepper.framework import AbstractComponent
from pepper.framework.sensor import VAD, SynchronousGoogleASR, StreamedGoogleASR, ASRHypothesis
from pepper import config

from threading import Thread

import numpy as np

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

        self._vad = VAD(self.backend.microphone)
        self._asr = SynchronousGoogleASR()

        def worker():
            for voice in self._vad:

                audio = voice.audio

                hypotheses = self.asr.transcribe(audio)
                if hypotheses:

                    # Call on_transcript Event Function
                    self.on_transcript(hypotheses, audio)

                    # Call Callback Functions
                    for callback in self.on_transcript_callbacks:
                        callback(hypotheses, audio)

        thread = Thread(target=worker, name="SynchronousSpeechRecognitionComponentWorker")
        thread.daemon = True
        thread.start()

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


class StreamedSpeechRecognitionComponent(SpeechRecognitionComponent):
    def __init__(self, backend):
        """
        Construct Speech Recognition Component

        Parameters
        ----------
        backend: Backend
        """
        super(StreamedSpeechRecognitionComponent, self).__init__(backend)

        self.on_transcript_callbacks = []
        self._asr = StreamedGoogleASR(config.APPLICATION_LANGUAGE, self.backend.microphone.rate)

        self._vad = VAD(self.backend.microphone)

        def worker():
            for voice in self._vad:
                hypotheses = self.asr.transcribe(voice)

                if hypotheses:
                    audio = voice.audio

                    # Call on_transcript Event Function
                    self.on_transcript(hypotheses, audio)

                    # Call Callback Functions
                    for callback in self.on_transcript_callbacks:
                        callback(hypotheses, audio)

        thread = Thread(target=worker, name="StreamingSpeechRecognitionComponentWorker")
        thread.daemon = True
        thread.start()

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
