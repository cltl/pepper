import sys; sys.path.append("..")

from pepper.app import App
from pepper.event import *

from pepper.image.camera import PepperCamera
from pepper.image.classify import ClassifyClient

from pepper.knowledge.wordnet import WordNet

from time import sleep
from random import choice
import os


GREETINGS = [
    "Hi",
    "Hello",
    "How are you?",
    "How are you doing?",
    "Hello there",
    "What's up",
    "Yo!",
    "Long time no see"
]


class iSpyApp(App):
    def __init__(self, address):
        super(iSpyApp, self).__init__(address)

        # Pepper services
        self.animated_speech = self.session.service("ALAnimatedSpeech")
        self.tactile_gesture = self.session.service("ALTactileGesture")
        self.speech_recognition = self.session.service("ALSpeechRecognition")
        self.camera = PepperCamera(self.session)

        # External services
        self.classify_client = ClassifyClient(('localhost', 9999))

        # Greetings
        # Subscribe to Looking at robot
        self.events.append(LookingAtRobotEvent(self.session, self.on_look))

        # Start game
        # Subscribe to Gesture detected
        self.events.append(GestureDetectedEvent(self.session, self.on_gesture)) #TODO-question: does this wait until on gesture is activated?
        # Subscribe to camera to look at objects on table/in room
        self.animated_speech.say("Let me see ...")
        self.events.append(self.camera)
        #TODO: Maybe direct camera towards objects?
        # Classify
        WORDS_SAID = self.classify(10)

        # Pick random object
        word = choice(WORDS_SAID)

        # Say hint
        #TODO:improve hint
        definition = WordNet.definitions(word)['noun'][0]
        print("Object chosen is {} -- {}".format(word, definition))
        self.animated_speech.say(r"I see something, which is {}".format(definition))

        # Receive guess
        guess = self.getGuessSpeech(self, WORDS_SAID)
        guess = self.getGuessCamera(self)

        print(guess)
        self.animated_speech.say(r'So you think the object I see is {}'.format(guess))

        # Robot gives feedback (yes/no)
        if guess == word:
            # Victory
            #TODO: victory dance

        else:
            # Guess again
            self.animated_speech.say(r"You guessed wrong. I will give you a second chance.")
            #TODO: select other hint
            hint = "dummy hint"
            self.animated_speech.say(r"I see something, which is {}".format(hint))


    # Event triggers
    def on_look(self, value):
        """
        When a person is looking at the robot, the robot greets them
        :param value: ID of person looking at robot
        """
        self.animated_speech.say(choice(GREETINGS))

    def on_gesture(self, value):
        """
        When a person touches the head of the robot, the robot stops greeting behavior to prepare for game
        :param value: gesture name
        """
        #TODO-check: Unsubscribe from LookingAtRobotEvent
        self.events[0].close() # events[0] should be LookingAtRobotEvent
        # Say that we start the game
        self.animated_speech.say("Let's play!")

    def on_word(self, words, wordDict):
        """
        When a word is recognized by the robot, it confirms what it heard
        :param words: raw list as returned by event
                wordDict: dictionary of vocabulary and confidence
        :return: word recognized
        """
        mostLikelyWord = words[0]
        print(wordDict)
        # TODO-check: return word with highest confidence
        return mostLikelyWord


    def classify(self, limit):
        """
        Method for classifying object that are seen by the robot camera
        :param limit: number of objects to be seen
        :return: set of words for objects seen
        """
        THRESHOLD = 0.4
        TMP = os.getcwd() + r'\capture.jpg'

        # Set of objects that have been observed
        WORDS_SAID = set()

        # Limit to 10 unique objects
        while len(WORDS_SAID) < limit:
            self.camera.get().save(TMP)
            for confidence, object in self.classify_client.classify(TMP):
                if confidence > THRESHOLD:
                    word = choice(object)
                    # Only add new objects to set #TODO: isn't this built in set behavior?
                    if word not in WORDS_SAID:
                        WORDS_SAID.add(word)
            sleep(1)
        return WORDS_SAID

    def getGuessSpeech(self, vocabulary):
        """
        Identify children guess based on what they say
        :param: set of words that can recognized
        :return: guess
        """
        self.speech_recognition.setLanguage("English")
        # Set vocabulary to list of objects
        self.animated_speech.say('I am listening')
        self.speech_recognition.setVocabulary(list(vocabulary), False)
        self.events.append(WordDetectedEvent(self.session, self.on_word))
        #TODO: get mostLikelyWord from on_word event
        return "dummy guess"

    def getGuessCamera(self):
        """
        Identify children guess based on what is shown in front of the camera
        :return: guess
        """
        guess = self.classify(1)
        return guess


if __name__ == "__main__":
    app = iSpyApp(["192.168.1.100", 9559])
    app.run()