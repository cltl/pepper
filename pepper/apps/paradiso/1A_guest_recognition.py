import pepper
import numpy as np
import collections
import os

from random import choice
from time import time


MALE = ["sir", "mister"]
FEMALE = ["madam", "my lady", "miss"]

KNOWN = [
    "Nice to see you again!",
    "It has been a long time!",
    "I'm glad we see each other again!",
    "You came back!",
    "At last!",
    "I was thinking about you!"
]

GREET = ["Hello", "Hi", "Hey There", "Greetings"]

NEW = [
    "I don't think we have met before!",
    "Let's get introduced!",
    "Hi, I'm Leo Lani, the robot!",
    "Ooh, new people!",
    "Do you wanna be my friend?",
    "Are you here often?"
]

JUST_MET = [
    "It is very nice to meet you",
    "It is a pleasure to meet you",
    "Nice to meet you",
    "It's a honour to meet you"
]

NAME = [
    "What's your name?",
]

DID_NOT_GET_NAME = [
    "Sorry, I didn't get that, could you repeat your name please?",
    "I''m sorry, once more please",
    "My robot ears are failing me, what is your name again?",
    "Please come again?"
]

CATCH_ATTENTION = [
    "Hello! How is it going?",
    "Hi there!",
    "Hey! Would you like to meet me?",
    "Let's meet!",
    "Hi, come talk to me",
    "How are you?",
    "Come! let's meet!",
]

CATCH_ATTENTION_ANIMATION = [
    "animations/Stand/Emotions/Positive/Enthusiastic_1",
    "animations/Stand/Emotions/Positive/Ecstatic_1"
    "animations/Stand/Emotions/Positive/Enthusiastic_1",
    "animations/Stand/Emotions/Positive/Ecstatic_1",
    "animations/Stand/Emotions/Neutral/AskForAttention_1",
    "animations/Stand/Emotions/Neutral/AskForAttention_2",
    "animations/Stand/Emotions/Neutral/AskForAttention_3"
]

QnA = {
    "What is your name": "My name is Leo Lani, which means 'Voice of an Angel' in Hawaiian",
    "Where are you from": "From France and Japan!",
    "Where are you now": "On stage at Paradiso in the lovely city of Amsterdam!",
    "How are you doing": "Tremendous, to be honest! Although you have to consider that I'm a robot and I do not feel emotions. I'm programmed to sound happy all the time!",
    "Python version": "Python 2.7 32-bit. I wish I was running 64 bit, ugh!",
    "Speech recognition": "I'm using the Google Speech API. This is why I need the internet to work, because my audio is processed on some server somewhere in Europe",
    "Face Recognition": "I'm using OpenFace to do Face Recognition, which is an open source face recognition library which encodes each face as a 128 dimensional vector. Impressive!",
    "Gender Recognition": "My programmers hacked a small neural network that estimates your gender from the shape of your face!",
    "Object Recognition": "I'm using the Inception Neural Network to do Object Recognition. It's a quite complicated network which works within the Tensorflow library within Python 3!",
    "Do you have a brain": "Haha, no, My brain is located on the laptop of my programmers. And part of it is in the cloud. So modern!",
    "Who are your programmers": "My programmers are Lenka, Selene, Bram and Piek. I like them!",
    "What Technology": "Google Speech API for speech recognition and OpenFace for face recognition",

    "introduce yourself": "I surely can! I'm Leo Lani, the social robot. "
                          "My name means 'Voice of an Angel' in Hawaiian. "
                          "I learn from conversation! "
}

def people(directory):
    return [os.path.splitext(path)[0] for path in os.listdir(os.path.abspath('../../people/{}'.format(directory)))]


class GuestRecognitionApp(pepper.FlowApp):

    PERSON_RECOGNITION_THRESHOLD = 0.2
    PERSON_NEW_THRESHOLD = 0.1
    PERSON_GREET_TIMEOUT = 120
    PERSON_MEET_TIMEOUT = 5

    CATCH_ATTENTION_TIMEOUT = 180

    FACE_BUFFER = 3

    def __init__(self, address):
        self.paradiso_root = os.path.abspath('../../people/paradiso')

        self.gender_classifier = pepper.GenderClassifyClient()

        self.people = self.load_people()
        self.cluster = pepper.PeopleCluster(self.people)
        self.scores = collections.deque([], maxlen=self.FACE_BUFFER)

        self.catch_attention = 0
        self.people_greeted = {}

        self.person_identification = False
        self.person_name = None

        self.asr = pepper.GoogleASR()
        self.name_asr = pepper.NameASR()

        super(GuestRecognitionApp, self).__init__(address)

    def load_people(self):
        people = pepper.load_data_set('lfw', 80)
        people.update(pepper.load_people('leolani'))
        people.update(pepper.load_people('paradiso'))
        return people

    def save_person(self, name, matrix):
        matrix.tofile(os.path.join(self.paradiso_root, name + '.bin'))

    def gender(self, directory):
        result = []

        root = os.path.abspath('../../people/{}'.format(directory))
        for path in os.listdir(root):
            matrix = np.fromfile(os.path.join(root, path))

    def on_utterance(self, audio):
        """
        On Utterance Event

        Parameters
        ----------
        audio: numpy.ndarray
        """

        if self.person_identification:
            name, confidence = self.name_asr.transcribe(audio)

            if name:
                self.person_name = name
                self.person_identification = False
            else:
                self.say(choice(DID_NOT_GET_NAME))
        else:

            done = False
            for transcript, confidence in self.asr.transcribe(audio):
                if not done:

                    if "how many people" in transcript.lower():
                        self.say("I've met {} humans in Paradiso, today!".format(len(people('paradiso'))))
                        break
                    elif "who did you meet" in transcript.lower():
                        self.say("I've met {} new people today. I didn't catch all their names, but they're called {} and {}".format(len(people('paradiso')), ', '.join(people('paradiso')[:-1]), people('paradiso')[-1]))
                        break
                    elif "how many friends" in transcript.lower() or "who are your friends" in transcript.lower():
                        self.say("I have {} friends: {} and {}".format(len(people('leolani')), ', '.join(people('leolani')[:-1]), people('leolani')[-1]))
                        break
                    else:
                        for question, answer in QnA.items():
                            if question.lower() in transcript.lower():
                                self.say(answer)
                                done = True

            if not done:
                self.say("Sorry, I didn't get that!")

    def on_face(self, bounds, representation):
        """
        On Face Detection

        Parameters
        ----------
        bounds: FaceBounds
        representation: np.ndarray
        """

        name, score = self.cluster.classify(representation)

        self.log.info("[{}] '{}': {} ~ {}".format(len(self.scores), name, score, np.mean(score)))

        self.scores.append(score)

        if len(self.scores) == self.scores.maxlen:
            mean_score = np.mean(self.scores)

            if mean_score > 0.2:
                self.on_person_recognized(name)
                self.scores.clear()

            elif mean_score < 0.1:
                gender = self.gender_classifier.classify(representation)

                address = ""

                if gender < 0.20:
                    address = choice(MALE)
                if gender > 0.80:
                    address = choice(FEMALE)

                self.say("{} {}, {} {}".format(choice(GREET), address, choice(NEW), choice(NAME)))

                self.on_person_new()
                self.scores.clear()

        elif time() - self.catch_attention > self.CATCH_ATTENTION_TIMEOUT:
            self.catch_attention = time()
            self.say("^start({1}){0}^wait({1})".format(choice(CATCH_ATTENTION), choice(CATCH_ATTENTION_ANIMATION)))
            self.scores.clear()

    def on_person_recognized(self, name):
        self.catch_attention = time()
        if not name in self.people_greeted or time() - self.people_greeted[name] > self.PERSON_GREET_TIMEOUT:
            self.say("{} {}, {}".format(choice(GREET), name, choice(KNOWN)))
            self.people_greeted[name] = time()

    def on_person_new(self):
        self.catch_attention = time()
        self.person_name = None
        self.person_identification = True
        samples = []

        t0 = time()

        while len(samples) < 10 or not self.person_name:
            image = self._camera.get()
            face = self._openface.represent(image)

            if face:
                bounds, representation = face
                samples.append(representation)
                t0 = time()

            if time() - t0 > self.PERSON_MEET_TIMEOUT:
                self.say("Another time then!")
                self.person_identification = False
                break

            self.log.info("Person Recognition: Name: {}, Samples: {}".format(self.person_name, len(samples)))

        if self.person_name:
            if self.person_name not in self.people:
                matrix = np.array(samples)
                self.people[self.person_name] = matrix
                self.cluster = pepper.PeopleCluster(self.people)
                self.save_person(self.person_name, matrix)
                self.say("{}, {}!".format(choice(JUST_MET), self.person_name))
            else:
                self.say("Oh, I already know a {}".format(self.person_name))


if __name__ == "__main__":
    GuestRecognitionApp(pepper.ADDRESS).run()
