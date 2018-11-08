from pepper.framework.abstract import AbstractComponent
from pepper.framework.component import SpeechRecognition
from threading import Thread
from time import sleep


class Statistics(AbstractComponent):
    def __init__(self, backend):
        """
        Construct Statistics Component

        Parameters
        ----------
        backend: Backend
        """
        super(Statistics, self).__init__(backend)

        speech_recognition = self.require_dependency(Statistics, SpeechRecognition)  # type: SpeechRecognition

        def worker():
            vad = speech_recognition.vad

            while True:
                activation_bars = int(vad.activation * 10)

                print "\rMicrophone {:3.1f} kHz | Camera {:4.1f} Hz | Voice {:12s} {:4s}".format(
                    self.backend.microphone._true_rate / 1000, self.backend.camera._true_rate,
                    ("<{:10s}>" if vad._voice else "[{:10s}]").format("|" * activation_bars + "." * (
                                10 - activation_bars)) if self.backend.microphone._running else "[          ]",
                    "{:4.0%}".format(vad.activation) if self.backend.microphone._running else "   %"
                ),
                sleep(0.1)

        thread = Thread(name="StatisticsThread", target=worker)
        thread.daemon = True
        thread.start()
