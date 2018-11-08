from pepper.framework import AbstractComponent, Application
from pepper.sensor import VAD, GoogleASR, StreamedGoogleASR
from pepper import config

from threading import Thread
from Queue import Queue


class SpeechRecognition(AbstractComponent):
    @property
    def asr(self):
        """
        Returns
        -------
        asr: pepper.sensor.asr.GoogleASR
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


class SynchronousSpeechRecognition(SpeechRecognition):
    def __init__(self, backend):
        """
        Construct Speech Recognition Component

        Parameters
        ----------
        backend: Backend
        """
        super(SynchronousSpeechRecognition, self).__init__(backend)

        self.on_transcript_callbacks = []
        self._asr = GoogleASR(config.LANGUAGE, self.backend.microphone.rate)

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
        asr: pepper.sensor.asr.GoogleASR
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


class StreamingSpeechRecognition(SpeechRecognition):
    _application = None  # type: Application

    def __init__(self, backend):
        """
        Construct Speech Recognition Component

        Parameters
        ----------
        backend: Backend
        """
        super(StreamingSpeechRecognition, self).__init__(backend)

        self.on_transcript_callbacks = []
        self._asr = StreamedGoogleASR(config.LANGUAGE, self.backend.microphone.rate)

        frame_queue = Queue()
        self._vad = VAD(self.backend.microphone, stream_callbacks=[
            lambda audio, speech: frame_queue.put((audio, speech))])

        def frame_generator():
            speech = True
            while speech:
                audio, speech = frame_queue.get()
                yield audio

        def worker():
            while True:
                audio, speech = frame_queue.get()

                if speech:
                    utterance = frame_generator()

                    hypotheses = self.asr.transcribe(utterance)

                    if hypotheses:

                        # Call on_transcript Event Function
                        self.on_transcript(hypotheses, audio)

                        # Call Callback Functions
                        for callback in self.on_transcript_callbacks:
                            callback(hypotheses, audio)

        thread = Thread(name="SpeechThread", target=worker)
        thread.daemon = True
        thread.start()

    @property
    def asr(self):
        """
        Returns
        -------
        asr: pepper.sensor.asr.GoogleASR
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