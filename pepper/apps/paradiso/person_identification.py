import pepper
import numpy as np
import collections

from random import choice


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

NAME = [
    "What's your name?",
    "Who are you?",
]


class PersonIdentificationApp(pepper.FlowApp):

    PERSON_RECOGNITION_THRESHOLD = 0.2
    PERSON_NEW_THRESHOLD = 0.1

    FACE_BUFFER = 3

    def __init__(self, address):

        self.gender_classifier = pepper.GenderClassifyClient()

        self.people = pepper.load_data_set('lfw', 80)
        self.people.update(pepper.load_people())
        self.cluster = pepper.PeopleCluster(self.people)

        self.scores = collections.deque([], maxlen=self.FACE_BUFFER)

        self.person_identification = False
        self.person_name = None

        self.asr = pepper.GoogleASR()
        self.name_asr = pepper.NameASR()

        super(PersonIdentificationApp, self).__init__(address)

    def on_utterance(self, audio):
        """
        On Utterance Event

        Parameters
        ----------
        audio: numpy.ndarray
        """

        if self.person_identification:
            hypothesis = self.name_asr.transcribe(audio)

            if hypothesis:
                name, confidence = hypothesis
                self.person_name = name
                self.person_identification = False
            else:
                self.say("Sorry, could you repeat that?")
        else:
            pass

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

                address = "human"

                if gender < 0.20:
                    address = choice(MALE)
                if gender > 0.80:
                    address = choice(FEMALE)

                self.say("{} {}, {} {}".format(choice(GREET), address, choice(NEW), choice(NAME)))

                self.on_person_new()
                self.scores.clear()

    def on_person_recognized(self, name):
        self.say("{} {}, {}".format(choice(GREET), name, choice(KNOWN)))

    def on_person_new(self):
        self.person_name = None
        self.person_identification = True
        samples = []

        while len(samples) < 10 or not self.person_name:
            image = self._camera.get()
            face = self._openface.represent(image)

            if face:
                bounds, representation = face
                samples.append(representation)

            self.log.info("Name: {}, Samples: {}".format(self.person_name, len(samples)))

        if self.person_name not in self.people:
            self.people[self.person_name] = np.array(samples)
            self.cluster = pepper.PeopleCluster(self.people)
            self.say("Nice to meet you, {}!".format(self.person_name))


if __name__ == "__main__":
    PersonIdentificationApp(pepper.ADDRESS).run()
