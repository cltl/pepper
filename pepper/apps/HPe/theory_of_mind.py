import pepper
from pepper.language import process_utterance as pu
from pepper.knowledge.theory_of_mind import TheoryOfMind
from pepper.apps.HPe.guest_recognition import QnA
from pepper.language.utils import UnknownPredicateError, IncompleteRDFError

import random
import re
from time import time

GREETINGS = [
    "Hey!",
    "Hello!",
    "Hi!",
    "How's it going?",
    "How are you doing?",
    "What's up?",
    "What's new?",
    "What's going on?",
    "What's up?",
    "Good to see you!",
    "Nice to see you!",
]

ASK_ME = [
    "Please ask me something!",
    "Ask me anything!",
    "I'm here for your questions!"
]


class TheoryOfMindApp(pepper.SensorApp):
    def __init__(self):
        super(TheoryOfMindApp, self).__init__(pepper.ADDRESS)

        random.seed(time())

        self.brain = TheoryOfMind()

        self.chat_turn = 0
        self.chat_id = 0

    def say(self, text, speed = 80):
        super(TheoryOfMindApp, self).say(text, speed)
        self.chat_turn += 1

    def on_utterance(self, audio):
        self.log.info("Utterance {:3.2f}s".format(float(len(audio)) / self.microphone.sample_rate))
        hypotheses = self._speech_to_text.transcribe(audio)

        if hypotheses:
            transcript, confidence = hypotheses[0]
            name_result = self.find_names(audio, hypotheses)

            if name_result:
                name, transcript, confidence = name_result

            self.on_transcript(transcript, self.current_person)

    def on_transcript(self, transcript, person):
        self.log.info("[{}] {} '{}'".format(self.chat_turn, person, transcript))

        for greeting in GREETINGS:
            if greeting[:-1].lower() in transcript.lower():
                self.say(random.choice(GREETINGS))
                return

        for question, answer in QnA.items():
            if question.lower() in transcript.lower():
                self.say(answer)
                return

        try:
            reply = pu.analyze_utterance(transcript, self.current_person, self.chat_id, self.chat_turn, self.brain)
            self.say(reply)
        except UnknownPredicateError as e:
            self.say(e.message)
        except IncompleteRDFError as e:
            self.say(e.message)

        self.chat_turn += 1

    def on_person_recognized(self, name):
        if name != self.current_person:
            self.say("{} {}!".format(random.choice(GREETINGS), name))
            self.say(random.choice(ASK_ME))
            self._current_person = name
            self.chat_id = int(random.getrandbits(128))
            self.chat_turn = 1

    def find_names(self, audio, hypotheses):
        NAME_REGEX = r' ([A-Z]\w+)'
        NAME_SUB = r'{0}'

        candidates = []

        for transcript, confidence in hypotheses:
            if not ' ' in transcript:
                candidates.append('{0}')
            else:
                transcript = re.sub(NAME_REGEX, ' {0}', transcript)
                if NAME_SUB in transcript:
                    candidates.append(transcript)

        if candidates:
            languages = ['en-GB', 'nl-NL']
            phrases = [candidates[0].format(name) for name in self._people.keys()]

            asrs = [pepper.GoogleASR(language=language, phrases=phrases) for language in languages]

            transcript, language, confidence = "", "", 0

            for asr, lang in zip(asrs, languages):
                hypotheses = asr.transcribe(audio)

                if hypotheses:
                    t, c = hypotheses[0]

                    if c > confidence:
                        transcript, language, confidence = t, lang, c

            names = re.findall(NAME_REGEX, transcript)

            if names:
                return names[0], transcript, confidence


if __name__ == "__main__":
    TheoryOfMindApp().run()
