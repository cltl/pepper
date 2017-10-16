from pepper.app import App
from pepper.speech.microphone import PepperMicrophone
from pepper.speech.recognition import GoogleRecognition
from pepper.knowledge.wolfram import SimpleWolfram
from pepper.event.sensors import GestureDetectedEvent
from pepper.output.led import *

from random import choice
import numpy as np


NO_RESULT_SPEECH = [
    "I have no clue, sorry",
    "I don't know",
    "You should look it up yourself!",
    "Google it!",
    "How would I know? I am a robot!"
]

class QueryApp(App):

    LISTEN_DURATION = 4

    def __init__(self, address):
        """
        Simple Application that let's you query Pepper for facts on a tap on his head.
        Natural Speech Recognition is done using the Google Speech API
            - Please make sure your environment is appropriately set up
        Knowledge is gathered from the WolframAlpha Spoken Results API, which is incredible :)

        Parameters
        ----------
        address: (str, int)
            Address of Pepper on the Network
        """

        super(QueryApp, self).__init__(address)

        self.speech = self.session.service("ALAnimatedSpeech")
        self.animation = self.session.service("ALAnimationPlayer")
        self.blinking = self.session.service("ALAutonomousBlinking")

        self.microphone = PepperMicrophone(self.session)
        self.recognition = GoogleRecognition()
        self.wolfram = SimpleWolfram()
        self.led = Led(self.session)

        self.events.append(GestureDetectedEvent(self.session, self.on_gesture))

    def on_gesture(self, name):
        """Program will fire when tapping on his head"""
        self.speech.say(u"Do you have a question for me?")

        # Random Eye Colors to show Pepper's Listening
        self.blinking.setEnabled(False)
        self.led.set(Leds.LEFT_FACE_LEDS, np.random.uniform(size=3).tolist())
        self.led.set(Leds.RIGHT_FACE_LEDS, np.random.uniform(size=3).tolist())

        # Get Audio for 'LISTEN_DURATION' seconds
        audio = self.microphone.get(self.LISTEN_DURATION)

        # Disable Random Eye Colors and Resume Blinking
        self.led.reset(Leds.LEFT_FACE_LEDS)
        self.led.reset(Leds.RIGHT_FACE_LEDS)
        self.blinking.setEnabled(True)

        # Transcribe Question and Obtain Confidence Level
        question, confidence = self.recognition.transcribe(audio)[0]
        # Query WolframAlpha for Answer to Question
        answer = self.wolfram.get(question)

        # Display Question
        print(u"Q: {} [{:3.0%}]".format(question, confidence))

        # Let Pepper Repeat Your Question
        self.speech.say(u"^startTag(estimate) You asked: {} ^waitTag(estimate)".format(question))

        if answer == "No spoken result available" or answer == "Wolfram Alpha did not understand your input":
            # In case Pepper does not know, he will ask you to 'Google it yourself'
            print(u"A: **NOT FOUND**\n")
            self.speech.say(u"^startTag(not know){}^waitTag(not know)".format(choice(NO_RESULT_SPEECH)))
        else:
            # Otherwise an answer will be provided
            print(u"A: {}\n".format(answer))
            self.speech.say(u"^startTag(explain){}^waitTag(explain)".format(answer))


if __name__ == "__main__":
    # Run App
    QueryApp(("192.168.1.101", 9559)).run()



