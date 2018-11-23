from pepper.framework import AbstractComponent, Application
from pepper.sensor import VAD, SynchronousGoogleASR, StreamedGoogleASR
from pepper import config

from threading import Thread
from Queue import Queue


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
    _application = None  # type: Application

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