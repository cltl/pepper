from __future__ import print_function

import threading
from sys import stdout, stderr
from time import time

from pepper.framework.abstract.component import AbstractComponent
from pepper.framework.component import SpeechRecognitionComponent
from pepper.framework.util import Scheduler
from pepper import logger


class StatisticsComponent(AbstractComponent):
    """
    Display Realtime Application Performance Statistics

    Parameters
    ----------
    backend: AbstractBackend
        Application Backend
    """

    PERFORMANCE_ERROR_THRESHOLD = 0.8

    LIVE_SPEECH = ""
    LIVE_SPEECH_TIMEOUT = 3
    LIVE_SPEECH_TIME = 0

    def __init__(self):
        # type: () -> None
        super(StatisticsComponent, self).__init__()

        self._log.info("Initializing StatisticsComponent")

        # Require Speech Recognition Component and Get Information from it
        speech_recognition = self.require(StatisticsComponent, SpeechRecognitionComponent)  # type: SpeechRecognitionComponent
        vad, asr = speech_recognition.vad, speech_recognition.asr()

        def worker():

            # Create Voice Activation Bar
            activation = int(vad.activation * 10)
            activation_print = "|" * activation + "." * (10 - activation)
            voice_print = ("<{:10s}>" if vad._voice else "[{:10s}]").format(activation_print)
            empty_voice_print = "[          ]"

            # Get Microphone Related Information
            mic_running = self.backend.microphone.running
            mic_rate = self.backend.microphone.rate
            mic_rate_true = self.backend.microphone.true_rate

            # Get Camera Related Information
            cam_rate = self.backend.camera.rate
            cam_rate_true = self.backend.camera.true_rate

            # If Camera and/or Microphone are not running as fast as expected -> show stderr message instead of stdout
            error = (cam_rate_true < cam_rate * self.PERFORMANCE_ERROR_THRESHOLD or
                     mic_rate_true < float(mic_rate) * self.PERFORMANCE_ERROR_THRESHOLD)

            # Show Speech to Text Transcript 'live' as it happens
            if asr.live:
                self.LIVE_SPEECH = asr.live
                self.LIVE_SPEECH_TIME = time()
            elif time() - self.LIVE_SPEECH_TIME > self.LIVE_SPEECH_TIMEOUT:
                self.LIVE_SPEECH = ""

            # Display Statistics
            print("\rThreads {:2d} | Cam {:4.1f} Hz | Mic {:4.1f} kHz | STT {:12s} >>> {}".format(
                threading.active_count(),
                cam_rate_true,
                mic_rate_true / 1000.0,
                voice_print if mic_running else empty_voice_print,
                self.LIVE_SPEECH),
                end="", file=(stderr if error else stdout))

        # Run 10 times a second
        # TODO: Bit Much?
        schedule = Scheduler(worker, 0.1)
        schedule.start()
        self._log.info("Started StatisticsComponent worker")
