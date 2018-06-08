import pepper
from random import choice

from pepper.apps.HPe.guest_recognition import QnA


ADDRESSING = [
    "Well, {}",
    "Look, {}",
    "I will tell you, {}",
    "I checked the internet, {}. This is what is says:",
    "I Googled it for you, {}.",
    "I found the answer on the interwebs, {}!"
]


SORRY = [
    "Sorry!",
    "I am sorry!",
    "Forgive me!",
    "My apologies!",
    "My humble apologies!",
    "How unfortunate!"
]

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

DONT_KNOW = [
    "I don't know",
    "I couldn't find it",
    "It is beyond my knowledge",
    "The internet didn't provide the data",
    "I don't know, sorry!",
    "Ask me another time, when I've gathered more knowledge",
    "How would I know, I am a robot!",
    "Please Google it yourself!",
    "I have no idea!",
    "Ask the internet!"
]


class WolframAlphaApp(pepper.SensorApp):
    def on_transcript(self, transcript, person):

        for question, answer in QnA.items():
            if question.lower() in transcript.lower():
                self.say(u"{} {}".format(choice(ADDRESSING).format(person), answer))
                return

        answer = pepper.Wolfram().query(transcript)

        if answer:
            self.say(u"{}, {}".format(choice(ADDRESSING).format(person), answer))
        else:
            self.say(u"{} {}, {}".format(choice(SORRY), person, choice(DONT_KNOW)))

    def on_person_recognized(self, name):
        if name != self.current_person:
            self.say(u"{}, {}!".format(choice(GREETINGS), name))
            self._current_person = name


if __name__ == "__main__":
    WolframAlphaApp(pepper.ADDRESS).run()
