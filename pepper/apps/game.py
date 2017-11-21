import sys; sys.path.append("..")

from pepper.app import App
from pepper.event import ObjectPresentEvent, GestureDetectedEvent

from threading import Thread
from time import sleep
from random import choice

VOICE_SPEED = 80
SAY_SPEED = "\RSPD=" + str(VOICE_SPEED) + "\ "

INTRODUCTION = """
Hello everybody, my name is Leo-lani! I am a social humanoid robot.
This means I can interact with you - through seeing, hearing, talking and moving.
However, in order to do anything - I need to be programmed. ...
Remember, a robot is only as smart as you make it to be!
Today, we will play a game. This is an opportunity for me to show all my skills.
I will think of an object I see, and give you hints to guess what I am thinking about...
I am excited to see how fast you can guess!
"""

OBJECT_HINTS = {
    'water bottle': [
        "It has a lid",
        "You cannot take it with you on an airplane",
        "It is made from plastic"
    ],
    'Granny Smith': [
        'You can eat it!',
        'It grows from trees',
        'It is healthy',
        'An electronic brand was named after it'
    ], #Granny Smith replaced banana
    'coffee mug': [
        'It holds drinks',
        "It's made from ceramic",
        "It has a handle"
    ],
    'sunglasses': [
        "You can use this object in summer",
        "You wear it on your head",
        "You don't use it indoors"
    ],
    'Christmas stocking': [
        "This is a holiday item",
        "You wear it when you are cold",
        "It has stripes"
    ],
    'stole': [
        "You wear it when it is cold",
        "It goes around your neck",
        "This object is usually made from wool"
    ],
    'goblet': [
        "You drink from it",
        "It can be made from glass or metal or plastic",
        "It is slim on the bottom but wide at the top"
    ],
    'teapot': [
        "You use it in the kitchen",
        "It can hold water inside",
        "It is a big object, maybe the size of your head!"
    ]
}



OBJECT_COLORS = {
    'water bottle': 'blue',
    'Granny Smith': 'green',
    'coffee mug': 'black',
    'sunglasses': 'black',
    'Christmas stocking': 'red',
    'stole': 'red',
    'goblet': 'transparent',
    'teapot': 'grey'
}

TEXT_SUCCESS = [
    "Congratulations, I was indeed looking for a {}. How very good of you",
    "Good job. it is indeed a {}",
    "Awesome, {} it is!",
    "You win! You can be proud of yourself by calling {}!",
    "{}! " * 3
]

TEXT_FAILURE = [
    "You are showing me a {}. This is, sadly, not what I was looking for",
    "Nope, it's not a {}. you wanna try again?",
    "It might look like a {}. But guess what! It's not!",
    "{}, I don't think so!!",
    "No, No, ... No No, not a {}!"
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
        print("Introduction")
        self.speech.say(SAY_SPEED + INTRODUCTION)

        # ..:: Runtime Variables ::.. #
        self.current_object = ""

        # ..:: Subscribe to Events ::.. #
        self.resources.append(GestureDetectedEvent(self.session, self.on_gesture))
        self.resources.append(ObjectPresentEvent(self.session, self.on_present, "PresentCamera5"))

        # Start Hinting
        hint_thread = Thread(target=self.hint)
        hint_thread.daemon = True
        hint_thread.start()

    def on_gesture(self, gesture_name):
        self.speech.say("Let's Play!")
        self.current_object = choice(OBJECT_COLORS.keys())
        color = OBJECT_COLORS[self.current_object]
        self.speech.say(SAY_SPEED + "I spy with my little eye... something which is... {}".format(color))

        print("Start Game: '{}'".format(self.current_object))

    def on_present(self, object_score, objects):
        if self.current_object:
            if object_score > 0.45:
                if self.current_object in objects:
                    animation = choice(ANIMATION_SUCCESS)
                    self.speech.say(SAY_SPEED + "^start({}){}^wait({})".format(
                        animation, choice(TEXT_SUCCESS).format(self.current_object), animation))

                    print("Success")
                    self.current_object = ""

                else:
                    animation = choice(ANIMATION_FAILURE)
                    self.speech.say(SAY_SPEED + "^start({}){}^wait({})".format(
                        animation, choice(TEXT_FAILURE).format(choice(objects)), animation
                    ))
                    print("Failure: '{}'".format(objects))

    def hint(self):
        while True:
            if self.current_object in OBJECT_HINTS:
                hint = choice(OBJECT_HINTS[self.current_object])
                self.speech.say("I have a hint! ... {}...".format(hint))
                print(SAY_SPEED + "Hint: '{}'".format(hint))
            sleep(20)

if __name__ == "__main__":
    app = Game(["192.168.1.103", 9559])
    app.run()
