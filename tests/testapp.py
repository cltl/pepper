import sys; sys.path.append("..")

from pepper.app import App
from pepper.event import *

from pepper.image.camera import PepperCamera
from pepper.image.classify import ClassifyClient

from pepper.knowledge.wordnet import WordNet

from threading import Thread
from time import sleep, time
from random import choice


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


class TestApp(App):
    def __init__(self, address):
        super(TestApp, self).__init__(address)

        self.animated_speech = self.session.service("ALAnimatedSpeech")

        self.camera = PepperCamera(self.session)

        self.classify_client = ClassifyClient(('localhost', 9999))

        self.events.append(FaceDetectedEvent(self.session, self.on_face))
        self.events.append(LookingAtRobotEvent(self.session, self.on_look))
        self.events.append(self.camera)

        classify_thread = Thread(target=self.classify)
        classify_thread.daemon = True
        classify_thread.start()

    def on_face(self, time, faces, recognition):
        pass

    def on_look(self, value):
        self.animated_speech.say(choice(GREETINGS))

    def classify(self):
        THRESHOLD = 0.4
        TMP = r'C:\Users\Bram\Documents\Pepper\pepper\tmp\capture.jpg'

        WORDS_SAID = set()

        while True:
            self.camera.get().save(TMP)
            for confidence, object in self.classify_client.classify(TMP):
                if confidence > THRESHOLD:

                    word = choice(object)

                    if word not in WORDS_SAID:
                        WORDS_SAID.add(word)

                        definition = WordNet.definitions(word)['noun'][0]
                        print("[{:3.0%}] {} -- {}".format(confidence, word, definition))
                        self.animated_speech.say(r"I see a {}, which is {}".format(word, definition))
                        sleep(5)
            sleep(1)


if __name__ == "__main__":
    app = TestApp(["192.168.1.101", 9559])
    app.run()