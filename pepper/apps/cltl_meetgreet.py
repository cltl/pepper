from pepper.app import App

from pepper.knowledge.wolfram import Wolfram
from pepper.knowledge.general_questions import general_questions
from pepper.knowledge.greetings import CATCH_ATTENTION, SIMPLE_GREETING

from pepper.event.people import FaceDetectedEvent, LookingAtRobotEvent
from pepper.speech.microphone import PepperMicrophone

from random import choice
from time import time



def brain(question):

    # Answer General Questions
    answer = general_questions(question)
    if answer: return answer

    # Query Wolfram Alpha
    answer = Wolfram().query(question)

    if answer:
        return answer.replace("Wolfram Alpha", "Leolani")
    else:
        return choice([
            "I have no clue, sorry",
            "I don't know",
            "You should look it up yourself!",
            "Google it!",
            "How would I know? I am a robot!",
            "I have no idea",
            "That is a very complex question for a simple robot like me"
        ])


class MeetGreet(App):

    SECONDS_BETWEEN_ATTENTIONS = 60
    SECONDS_BETWEEN_GREETINGS = 60

    def __init__(self, address):
        super(MeetGreet, self).__init__(address)

        # Services
        self.microphone = PepperMicrophone(self.session)
        self.speech = self.session.service("ALAnimatedSpeech")

        # Variables
        self.busy = False
        self.last_attention_time = 0
        self.last_greeting_time = 0

        # Events
        self.resources.append(FaceDetectedEvent(self.session, self.on_face))
        self.resources.append(LookingAtRobotEvent(self.session, self.on_look))

        self.log.info("Application Started")

    def on_face(self, t, faces, recognition):
        if not self.busy and time() - self.last_attention_time > self.SECONDS_BETWEEN_ATTENTIONS:
            # TODO: Attention!
            self.last_attention_time = time()

    def on_look(self, person, score):
        if not self.busy and time() - self.last_greeting_time > self.SECONDS_BETWEEN_GREETINGS:
            # TODO: Greet!
            self.last_attention_time = time()
            self.last_greeting_time = time()




