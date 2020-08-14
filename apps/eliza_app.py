"""Example Application that answers questions posed in natural language using Wikipedia"""
from time import sleep

from pepper import config  # Global Configuration File
from pepper.app_container import ApplicationContainer
from pepper.framework.abstract import AbstractApplication, AbstractIntention
from pepper.framework.component import StatisticsComponent, SpeechRecognitionComponent, TextToSpeechComponent
from pepper.knowledge import animations
# TODO Unresolved import
from pepper.responder import eliza

SPEAKER_NAME_THIRD = "Dear patient"
SPEAKER_NAME = "Dear patient"
SPEAKER_FACE = "HUMAN"
DEFAULT_SPEAKER = "Human"
NAME = "Sigmund Freud"

MIN_ANSWER_LENGTH = 4
# Override Speech Speed for added clarity!
config.NAOQI_SPEECH_SPEED = 80


class ElizaApplication(ApplicationContainer,
                       AbstractApplication,         # Every Application Inherits from AbstractApplication
                       StatisticsComponent,         # Displays Performance Statistics in Terminal
                       SpeechRecognitionComponent,  # Enables Speech Recognition and the self.on_transcript event
                       TextToSpeechComponent):      # Enables Text to Speech and the self.say method

    SUBTITLES_URL = "https://bramkraai.github.io/subtitle?text={}"


    def __init__(self):
        """Greets New and Known People"""
        self.name_time = {}  # Dictionary of <name, time> pairs, to keep track of who is greeted when

        super(ElizaApplication, self).__init__()

        IntroductionIntention(self).speech()
        sleep(2.5)


    def show_text(self, text):
        text_websafe = text
        # text_websafe = urllib.quote(''.join([i for i in re.sub(r'\\\\\S+\\\\', "", text) if ord(i) < 128]))
        self.backend.tablet.show(self.SUBTITLES_URL.format(text_websafe))

    def on_transcript(self, hypotheses, audio):
        """
        On Transcript Event.
        Called every time an utterance was understood by Automatic Speech Recognition.

        Parameters
        ----------
        hypotheses: List[ASRHypothesis]
            Hypotheses about the corresponding utterance
        audio: numpy.ndarray
            Utterance audio
        """

        # Choose first ASRHypothesis and interpret as question
        for h in hypotheses:
            question = h.transcript
            self.show_text(question)

            answer = eliza.analyze(question)

            if answer:
                print("You said:", question)
                # Tell Answer to Human
                self.show_text(answer)
                self.say(answer)
                break


class IntroductionIntention(AbstractIntention, ElizaApplication):
    def speech(self):
        # 1.1 - Welcome
        self.say("Hello. Welcome to my clinic", animations.BOW)
        self.say("My name is "+NAME)
        self.say("I am your best friend and personal therapist", animations.MODEST)
        self.say("How do you feel today?", animations.FRIENDLY)
        sleep(3.5)


if __name__ == "__main__":
    application = ElizaApplication()
    application.run()
