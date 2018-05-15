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

SENTENCES_LENKA = [
    " ",
    "I know Piek, Selene, another Selene, Bram. And I know you, Lenka!",
    "Byebye!"
]

SENTENCES_BRAM = [
]

NAME = [
    "What's your name?",
    "Who are you?",
]


class ConversationApp(pepper.FlowApp):

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
        self.current_person = None

        self.asr = pepper.GoogleASR()
        self.name_asr = pepper.NameASR()

        self.index = 0

        super(ConversationApp, self).__init__(address)

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
            hypotheses = self.asr.transcribe(audio)

            if hypotheses:
                if self.current_person == 'Lenka' and self.index < len(SENTENCES_LENKA):
                    self.say(SENTENCES_LENKA[self.index])
                    self.index += 1

                if self.current_person == 'Bram' and self.index < len(SENTENCES_BRAM):
                    self.say(SENTENCES_BRAM[self.index])
                    self.index += 1

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
        if name != self.current_person:
            self.say("{} {}, {}".format(choice(GREET), name, choice(KNOWN)))
            self.current_person = name

            # if self.current_person == 'Lenka':
            #     self.say("Where are you from?")
            # if self.current_person == "Bram":
            #     self.say("What movies do you like?")

            self.index = 0

    def on_person_new(self):
        pass


if __name__ == "__main__":
    ConversationApp(pepper.ADDRESS).run()
