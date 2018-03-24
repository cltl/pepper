import pepper
import collections
import numpy as np
from time import time
from random import choice


KNOW_PERSON = [
    "Nice to see you again!",
    "It has been a long time!",
    "I'm glad we see each other again!",
    "You came back!",
    "At last!",
    "I was thinking about you!"
]

GREET_PERSON = ["Hello", "Hi", "Hey There", "Greetings"]

NO_ANSWER = [
    "I don't know, sorry!",
    "Ask me another time, when I've gathered more knowledge",
    "How would I know, I am a robot!",
    "Please Google it yourself!",
    "I have no idea!",
    "Ask the internet!"
]


class WolframApp(pepper.FlowApp):

    FACE_BUFFER = 3
    PERSON_GREET_TIMEOUT = 180

    def __init__(self, address):
        super(WolframApp, self).__init__(address)

        self.asr = pepper.GoogleASR()
        self.wolfram = pepper.Wolfram()

        self.people = self.load_people()
        self.cluster = pepper.PeopleCluster(self.people)
        self.scores = collections.deque([], maxlen=self.FACE_BUFFER)

        self.people_greeted = {}

    def load_people(self):
        people = pepper.load_data_set('lfw', 80)
        people.update(pepper.load_people('leolani'))
        people.update(pepper.load_people('paradiso'))
        return people

    def on_utterance(self, audio):
        hypotheses = self.asr.transcribe(audio)

        if hypotheses:
            question, confidence = hypotheses[0]
            answer = self.wolfram.query(question)
            if answer: self.say("You asked {}. {}".format(question, answer.encode('ascii', 'ignore').replace("Wolfram Alpha", "Leo Lani")))
            else: self.say(choice(NO_ANSWER))

    def on_face(self, bounds, representation):
        name, score = self.cluster.classify(representation)

        self.log.info(u"[{}] '{}': {} ~ {}".format(len(self.scores), name, score, np.mean(score)))

        self.scores.append(score)

        if len(self.scores) == self.scores.maxlen:
            mean_score = np.mean(self.scores)

            if mean_score > 0.2:
                self.on_person_recognized(name)
                self.scores.clear()

    def on_person_recognized(self, name):
        if not name in self.people_greeted or time() - self.people_greeted[name] > self.PERSON_GREET_TIMEOUT:
            self.say("{} {}, {}".format(choice(GREET_PERSON), name, choice(KNOW_PERSON)))
            self.people_greeted[name] = time()


if __name__ == "__main__":
    WolframApp(pepper.ADDRESS).run()
