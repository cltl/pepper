from pepper.app import App

from pepper.knowledge.wolfram import Wolfram
from pepper.knowledge.general_questions import general_questions
from pepper.knowledge.greetings import CATCH_ATTENTION, SIMPLE_GREETING

from pepper.speech.microphone import PepperMicrophone
from pepper.speech.recognition import GoogleStreamedRecognition

from pepper.vision.camera import PepperCamera, Resolution
from pepper.vision.classification.face import FaceRecognition

from pepper.output.led import *

from pepper.event.people import FaceDetectedEvent, LookingAtRobotEvent

from random import choice
from time import time, sleep

import numpy as np


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
    SECONDS_BETWEEN_GREETINGS = 10
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
        self.camera = PepperCamera(self.session, "PepperCamera6", Resolution.QVGA)
        self.led = Led(self.session)

        self.speech = self.session.service("ALAnimatedSpeech")
        self.speech_to_text = None
        self.face_recognition = FaceRecognition()

        # Variables
        self.last_attention_time = 0
        self.last_greeting_time = 0

        # State
        self.listening = False
        self.answering = False
        self.greeting = False

        # Events
        self.resources.append(FaceDetectedEvent(self.session, self.on_face))
        self.resources.append(LookingAtRobotEvent(self.session, self.on_look))

        self.log.info("Application Started")

    @property
    def busy(self):
        return self.listening or self.answering or self.greeting

    def on_face(self, t, faces, recognition):
        if not self.busy and time() - self.last_attention_time > self.SECONDS_BETWEEN_ATTENTIONS:
            self.greeting = True

            self.log.info("on_face event")
            self.speech.say("\\rspd=90\\^start({0}) {1} ^stop({0})".format(
                choice(CATCH_ATTENTION['ANIMATIONS']), choice(CATCH_ATTENTION['TEXT'])))
            self.last_attention_time = time()

            self.greeting = False

    def on_look(self, person, score):
        if not self.busy and time() - self.last_greeting_time > self.SECONDS_BETWEEN_GREETINGS:
            self.greeting = True

            self.log.info("on_look_event")

            # Get Gender of Person for Appropriate Greeting
            image = self.camera.get()
            person = self.face_recognition.representation(image)

            PERSON_TAG = ""

            if person:
                bounds, representation = person
                gender, probability = self.face_recognition.gender(representation)

                if gender: PERSON_TAG = choice(['Madam', "My Lady", "Mam"])
                else: PERSON_TAG = choice(["Sir", "Mister"])

            # General Attention Calling
            self.speech.say("\\rspd=90\\^start({0}) {1}, {2} ^stop({0})".format(
                choice(SIMPLE_GREETING['ANIMATIONS']), choice(SIMPLE_GREETING['TEXT']), PERSON_TAG
            ))
            self.last_attention_time = time()
            self.last_greeting_time = time()

            # Ask for Question
            self.speech.say("\\rspd=90\\{}".format(choice(self.ASK_FOR_QUESTION)))
            self._listen()

            self.greeting = False

    def on_speech(self, hypotheses, final):
        question, confidence = hypotheses[0]

        if final:
            self.answering = True
            self.listening = False

            self.log.info(u"Q: {}".format(question))
            self.led.set(Leds.LEFT_FACE_LEDS, [0.2, 0.2, 1])
            self.led.set(Leds.RIGHT_FACE_LEDS, [0.2, 0.2, 1])
            answer = brain(question)
            self.led.set(Leds.LEFT_FACE_LEDS, [0.2, 1, 0.2])
            self.led.set(Leds.RIGHT_FACE_LEDS, [0.2, 1, 0.2])
            self.log.info(u"A: {}".format(answer))

            self.speech.say("\\rspd=90\\{}".format(answer))

            self.answering = False
        else:
            color = np.random.uniform(size=3).tolist()
            color[2] = 1

            self.led.set(Leds.LEFT_FACE_LEDS, color)
            self.led.set(Leds.RIGHT_FACE_LEDS, color)

    def _listen(self):
        self.log.info("Listening for Speech")
        self.listening = True
        self.speech_to_text = GoogleStreamedRecognition(self.microphone, self.on_speech)
        sleep(self.SECONDS_LISTENING_FOR_QUESTION)
        self.speech_to_text.stop()
        self.listening = False



if __name__ == "__main__":
    MeetGreet(["192.168.1.103", 9559]).run()