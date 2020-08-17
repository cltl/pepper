from threading import Thread

import numpy as np
from typing import *

from pepper.framework.abstract.component import AbstractComponent
from pepper.framework.sensor.api import UtteranceHypothesis
from pepper import logger

class SpeechRecognitionComponent(AbstractComponent):
    """
    Speech Recognition Component. Exposes on_transcript Event to Applications.
    """

    def __init__(self):
        # type: () -> None
        super(SpeechRecognitionComponent, self).__init__()

        self._log.info("Initializing SpeechRecognitionComponent")

        # Public List of On Transcript Callbacks:
        # Allowing other Components to Subscribe to it
        self.on_transcript_callbacks = []

        def worker():
            # type: () -> None
            """Speech Transcription Worker"""

            # Every time a voice has been registered by the Voice Activity Detection (long running generator)
            for voice in self.vad:

                # Transcribe this Voice and obtain a number of UtteranceHypotheses
                hypotheses = self.asr().transcribe(voice)

                if hypotheses:

                    # Get Voice Audio Corresponding with Hypotheses
                    audio = voice.audio

                    # Call on_transcript Event Function
                    self.on_transcript(hypotheses, audio)

                    # Call Callback Functions
                    for callback in self.on_transcript_callbacks:
                        callback(hypotheses, audio)

        # TODO: Make into Schedule to give breathing room to other Threads? (Python GIL)
        thread = Thread(target=worker, name="StreamingSpeechRecognitionComponentWorker")
        thread.daemon = True
        thread.start()
        self._log.info("Started SpeechRecognitionComponent worker")

    def on_transcript(self, hypotheses, audio):
        # type: (List[UtteranceHypothesis], np.ndarray) -> NoReturn
        """
        On Transcript Event. Called every time an utterance was understood by Automatic Speech Recognition.

        Parameters
        ----------
        hypotheses: List[UtteranceHypothesis]
            Hypotheses about the corresponding utterance
        audio: numpy.ndarray
            Utterance audio
        """
        pass
