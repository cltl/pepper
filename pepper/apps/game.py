import sys; sys.path.append("..")

from pepper.app import App
from pepper.event import ObjectPresentEvent, GestureDetectedEvent

from pepper.image.camera import PepperCamera
from pepper.image.classify import ClassifyClient
from pepper.knowledge.wordnet import WordNet

from threading import Thread, Timer
from time import sleep
from random import choice

INTRODUCTION = """
    Hello, I am Pepper.
"""

OBJECT_HINTS = {
    'water bottle': [
        "It has a lid",
        "You cannot take it with you on an airplane",
        "It is made from plastic"
    ],
    'banana': [
        'You can eat it!',
        'It grows from trees',
        'It can be peeled'
    ],
    'coffee mug': [
        'It holds drinks',
        "It's made from ceramic",
        "It has a handle"
    ],
    'water jug': [
        "It holds water",
        "You use it in the garden",
        "It has a handle"
    ],
}

OBJECT_COLORS = {
    'water bottle': 'blue',
    'banana': 'yellow',
    'coffee mug': 'black',
    'water jug': 'white',
}

TEXT_SUCCESS = [
    "Congratulations, I was indeed looking for a {}. How very good of you"
]

TEXT_FAILURE = [
    "You are showing me a {}. This is, sadly, not what I was looking for"
]

ANIMATION_FAILURE = [
    "animations/Stand/Gestures/Reject_1",
    "animations/Stand/Gestures/Reject_2",
    "animations/Stand/Gestures/Reject_3",
    "animations/Stand/Gestures/Reject_4",
    "animations/Stand/Gestures/Reject_5"
]

ANIMATION_SUCCESS = [
    "animations/Stand/Emotions/Positive/Happy_1",
    "animations/Stand/Emotions/Positive/Happy_2",
    "animations/Stand/Emotions/Positive/Happy_3",
    "animations/Stand/Emotions/Positive/Happy_4"
]


class Game(App):

    CLASSIFICATION_SERVICE_ADDRESS = ('localhost', 9999)

    def __init__(self, address):
        super(Game, self).__init__(address)

        # Get Pepper's Animated Speech Service
        # This enables Pepper to perform Text-To-Speech while animating his body
        self.speech = self.session.service("ALAnimatedSpeech")

        # ..:: Introduction ::.. #
        self.speech.say(INTRODUCTION)

        # ..:: Runtime Variables ::.. #
        self.recognised_objects = set()
        self.current_object = ""

        # ..:: Subscribe to Events ::.. #
        self.events.append(GestureDetectedEvent(self.session, self.on_gesture))
        self.events.append(ObjectPresentEvent(self.session, self.on_present, "PresentCamera"))

        # Start Hinting
        hint_thread = Thread(target=self.hint)
        hint_thread.daemon = True
        hint_thread.start()

    def on_gesture(self, gesture_name):
        self.speech.say("Let's Play!")

        self.current_object = choice(OBJECT_COLORS.keys())
        hint = OBJECT_COLORS[self.current_object] if self.current_object in OBJECT_COLORS else \
            WordNet.definitions(self.current_object)['noun'][0]

        self.speech.say("I spy with my little eye something which is {}".format(
            hint))

    def on_present(self, object_score, object):
        if self.current_object:
            if object_score > 0.6:
                if self.current_object in object:
                    animation = choice(ANIMATION_SUCCESS)
                    self.speech.say("^start({}){}^wait({})".format(
                        animation, choice(TEXT_SUCCESS).format(self.current_object), animation))
                    self.current_object = ""

                else:
                    animation = choice(ANIMATION_FAILURE)
                    self.speech.say("^start({}){}^wait({})".format(
                        animation, choice(TEXT_FAILURE).format(choice(object)), animation
                    ))

    def hint(self):
        while True:
            if self.current_object in OBJECT_HINTS:
                self.speech.say("I have a hint! {}".format(choice(OBJECT_HINTS[self.current_object])))
            sleep(15)

if __name__ == "__main__":
    app = Game(["192.168.1.100", 9559])
    app.run()
