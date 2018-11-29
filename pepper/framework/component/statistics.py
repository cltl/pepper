from pepper.framework.abstract import AbstractComponent
from pepper.framework.util import Scheduler
from pepper.framework.component.speech_recognition import SpeechRecognitionComponent


class StatisticsComponent(AbstractComponent):
    def __init__(self, backend):
        """
        Construct Statistics Component

        Parameters
        ----------
        backend: Backend
        """
        super(StatisticsComponent, self).__init__(backend)

        speech_recognition = self.require_dependency(StatisticsComponent, SpeechRecognitionComponent)  # type: SpeechRecognitionComponent
        vad = speech_recognition.vad

        def worker():
            activation_bars = int(vad.activation * 10)

            print "\rMicrophone {:3.1f} kHz | Camera {:4.1f} Hz | Voice {:12s} {:4s}".format(
                self.backend.microphone.true_rate / 1000.0, self.backend.camera.true_rate,
                ("<{:10s}>" if vad._voice else "[{:10s}]").format("|" * activation_bars + "." * (
                            10 - activation_bars)) if self.backend.microphone.running else "[          ]",
                "{:4.0%}".format(vad.activation) if self.backend.microphone.running else "   %"),

        schedule = Scheduler(worker, 0.1)
        schedule.start()
