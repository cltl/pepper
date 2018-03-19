import pepper
import numpy as np
import collections
import os
from random import choice

from pepper.language.analyze_utterance import analyze_utterance


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


class TheoryOfMindApp(pepper.FlowApp):

    PERSON_RECOGNITION_THRESHOLD = 0.2
    PERSON_NEW_THRESHOLD = 0.1
    PERSON_GREET_TIMEOUT = 120
    FACE_BUFFER = 3

    NAME_FINDING_TRIALS = 3

    def __init__(self, address):
        self.paradiso_root = os.path.abspath('../../people/paradiso')

        self.gender_classifier = pepper.GenderClassifyClient()

        self.people = self.load_people()
        self.cluster = pepper.PeopleCluster(self.people)
        self.scores = collections.deque([], maxlen=self.FACE_BUFFER)

        self.current_person = None
        self.current_person_confidence = 0

        self.asr = pepper.GoogleASR(max_alternatives=self.NAME_FINDING_TRIALS)
        self.name_recognition = pepper.NameRecognition()

        super(TheoryOfMindApp, self).__init__(address)

    def load_people(self):
        people = pepper.load_data_set('lfw', 80)
        people.update(pepper.load_people('leolani'))
        people.update(pepper.load_people('paradiso'))
        return people

    def on_transcript(self, audio, transcript, transcript_confidence, name, name_confidence):
        self.log.info('{}: "{}"'.format(name, transcript))
        self.say(analyze_utterance(transcript, name.lower() if name else "person"))

    def on_utterance(self, audio):
        """
        On Utterance Event

        Parameters
        ----------
        audio: numpy.ndarray
        """
        self._utterance.stop()

        hypotheses = self.asr.transcribe(audio)

        if hypotheses:

            # Get the most likely Hypothesis
            for transcript, confidence in hypotheses:
                name_transcript = self.name_recognition.recognize(transcript)

                if '{}' in name_transcript:
                    name, name_confidence = pepper.NameASR(hints=(name_transcript,)).transcribe(audio)
                    name_transcript = name_transcript.format(name)
                    self.on_transcript(audio, name_transcript, confidence, self.current_person, self.current_person_confidence)
                    break
            else:
                self.on_transcript(audio, hypotheses[0][0], hypotheses[0][1], self.current_person, self.current_person_confidence)

        self._utterance.start()

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
                self.on_person_recognized(name, score)
                self.scores.clear()

    def on_person_recognized(self, name, confidence):
        if name != self.current_person:  # Only trigger when known person changes
            self.log.info("Recognized '{}' with Silhouette Score: {}".format(name, confidence))

            # Update Current Person, to which on_transcript will be attributed
            self.current_person = name
            self.current_person_confidence = confidence

            # Greet Person and ask Question
            self.say("{} {}, {}".format(choice(GREET), name, choice(KNOWN)))

    def on_person_new(self):
        pass


if __name__ == "__main__":
    TheoryOfMindApp(pepper.ADDRESS).run()
