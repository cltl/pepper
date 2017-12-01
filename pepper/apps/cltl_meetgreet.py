from pepper.app import App

from pepper.knowledge.wolfram import Wolfram
from pepper.knowledge.general_questions import general_questions
from pepper.knowledge.greetings import CATCH_ATTENTION, SIMPLE_GREETING

from pepper.event.people import FaceDetectedEvent, LookingAtRobotEvent
from pepper.speech.microphone import PepperMicrophone
from pepper.speech.recognition import GoogleUtterance

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
    SECONDS_LISTENING_FOR_QUESTION = 30

    ASK_FOR_QUESTION = [
        "I'm listening",
        "Shoot me a question",
        "What would you like to know?",
        "What's your question?",
        "I am ready for your question",
        "Ask me",
        "Let's hear your question"
    ]

    def __init__(self, address):
        super(MeetGreet, self).__init__(address)

        # Services
        self.microphone = PepperMicrophone(self.session)
        self.speech = self.session.service("ALAnimatedSpeech")
        self.recognition = GoogleUtterance(self.microphone)

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
            self.busy = True
            self.log.info("on_face event")
            self.speech.say("^start({0}) {1} ^stop({0})".format(
                choice(CATCH_ATTENTION['ANIMATIONS']), choice(CATCH_ATTENTION['TEXT'])))
            self.last_attention_time = time()
            self.busy = False

    def on_look(self, person, score):
        if not self.busy and time() - self.last_greeting_time > self.SECONDS_BETWEEN_GREETINGS:
            self.busy = True
            self.speech.say("^start({0}) {1} ^stop({0})".format(
                choice(SIMPLE_GREETING['ANIMATIONS']), choice(SIMPLE_GREETING['TEXT'])
            ))
            self.last_attention_time = time()
            self.last_greeting_time = time()
            self.busy = False

        self.speech.say(self.ASK_FOR_QUESTION)

        question = self.recognition.listen(self.SECONDS_LISTENING_FOR_QUESTION)
        self.log.info("Q: {}".format(question))

        answer = brain(question)
        self.log.info("A: {}".format(question))

        self.speech.say(answer)


if __name__ == "__main__":
    MeetGreet(["192.168.1.102", 9559]).run()