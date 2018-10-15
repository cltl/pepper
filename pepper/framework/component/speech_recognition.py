from pepper.framework.abstract import AbstractComponent
from pepper.sensor import VAD, GoogleASR
from pepper import config


class SpeechRecognition(AbstractComponent):
    def __init__(self, backend):
        """
        Construct Speech Recognition Component

        Parameters
        ----------
        backend: Backend
        """
        super(SpeechRecognition, self).__init__(backend)

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
