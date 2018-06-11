import pepper
from time import time, sleep
import numpy as np
import re
import os

from random import choice
from datetime import datetime
import requests

from pepper.knowledge.news import get_random_headline_speech



EVENT = "HPe"
LOCATION = requests.get('http://ipinfo.io/json').json()['city']

def n_friends():
    return "I have {} friends!".format(len(pepper.PeopleClassifier.load_directory('leolani')))

def n_people():
    n_people = len(pepper.PeopleClassifier.load_directory(EVENT))
    return "I've met {} people today!".format(n_people) if n_people > 1 else "I've just met one person today!"

def friends():
    friends = pepper.PeopleClassifier.load_directory('leolani').keys()
    return "My friends are {} and {}.".format(", ".join(friends[:-1]), friends[-1])

def people():
    p = pepper.PeopleClassifier.load_directory(EVENT).keys()

    if len(p) > 1:
        return "I've met several people today: {} and {}".format(", ".join(p[:-1]), p[-1])
    else:
        return "I've had the honour to meet {}!".format(p[0])


QnA_DYNAMIC = {
    "news": get_random_headline_speech,
    "What time is it": lambda: datetime.now().strftime("It is currently %H:%M"),
    "The time": lambda: datetime.now().strftime("It is currently %H:%M"),
    "How many friends": n_friends,
    "Who are your friends": friends,
    "How many people": n_people,
    "Who did you meet": people,
}

QnA_STATIC = {
    "Where are we": "I feel in my Wifi that we are in {}".format(LOCATION),

    "Open Source": "Yes, The code I'm running on is fully Open Source, you can find it on GitHub!",
    "tell me a joke": "Ok! \\pau=500\\ What's the difference between a hippo? \\pau=500\\ and a Zippo? \\pau=2000\\ Well \\pau=100\\, one is really heavy and the other is a little lighter.",

    "What is your name": "My name is Leo Lani, which means \\vct=70\\ 'Voice of an Angel' \\vct=100\\ in Hawaiian",
    "Where are you from": "From France and Japan!",
    "How old are you": "I was born on Tuesday the eleventh of July, 2017. That means I'm 11 months old",
    "When was your first performance": "My first performance was on July thirteenth, 2017! It was recorded on TV!",
    "did you like it": "Definitely",
    "male or female": "I'm female, and proud of it!",
    "Are you male": "Nope, I am a Lady!",
    "Are you female": "Yes, indeed!",
    "gender": "I'm female!",
    "How are you doing": "Tremendous, to be honest! Although you have to consider that I'm a robot and I do not feel emotions. I'm programmed to sound happy all the time!",
    "Python version": "Python 2.7 32-bit. I wish I was running 64 bit, ugh!",
    "Speech Recognition": "I'm using the Google Speech API. This is why I need the internet to work, because my audio is processed on some server somewhere in Europe",
    "Face Recognition": "I'm using OpenFace to do Face Recognition, which is an open source face recognition library which encodes each face as a 128 dimensional vector. Impressive!",
    "Object Recognition": "I'm using the Inception Neural Network to do Object Recognition. It's a quite complicated network which works within the Tensorflow library within Python 3!",
    "Do you have a brain": "Haha, no, My brain is located on the laptop of my programmers. And part of it is in the cloud. So modern!",
    "Who are your programmers": "My programmers are Lenka, Selene, Bram and Piek. I like them!",
    "What Technology": "Google Speech API for speech recognition and OpenFace for face recognition",

    "introduce yourself": "I surely can! I'm Leo Lani, the social robot. "
                          "My name means 'Voice of an Angel' in Hawaiian. "
                          "I learn from conversation! "
}


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

TELL_KNOWN = [
    "Nice to see you again!",
    "It has been a long time!",
    "I'm glad we see each other again!",
    "You came back!",
    "At last!",
    "I was thinking about you!"
]

INTRODUCE = [
    "My name is Leo Lani!",
    "I'm Leo Lani.",
    "I am Leo Lani.",
    "I am a Pepper robot.",
    "I am a social robot.",
]

ASK_NAME = [
    "What is your name?",
    "Who are you?",
    "I've told you my name, but what about yours?",
    "I would like to know your name!",
    "Can you tell me your name",
]

VERIFY_NAME = [
    "So you are called {}?",
    "Ah, your name is {}?",
    "Did I hear correctly your name is {}?",
    "I'm not sure, but is your name {}?",
    "Ok, is it {} then?"
]

DIDNT_HEAR_NAME = [
    "I didn't get your name.",
    "Sorry, I didn't get that.",
    "Oops, I didn't get your name.",
]

REPEAT_NAME = [
    "Could you repeat your name please?",
    "What is your name again?",
    "What did you say your name was?",
    "I don't understand single words that well, please try a sentence instead!",
    "I'm not good with all names, maybe try an English nickname if you will!",
    "Sorry, names are not my strong point",
]

JUST_MET = [
    "Nice to meet you, {}!",
    "It's a pleasure to meet you, {}!",
    "I'm happy to meet you, {}!",
    "Great we can be friends, {}!",
    "I hope we'll talk more often, {}!",
    "See you again soon, {}!"
]

MORE_SAMPLES = [
    "Let me have a good look at you, so I'll remember you!",
    "Can you show me your face, please? Then I'm sure I'll recognize you later",
    "Please let me have a look at you, then I'll know who you are!",
]

LOST_FACE = [
    "Oh, I lost you. Let's meet another time then!",
    "I got distracted, better next time!",
    "Ok, byebye, I'll meet you another time.",
    "Bye, There's time to meet later, I think!",
    "I'm confused, I hope you want to meet me later?",
]

DIFFERENT_FACE = [
    "Oh, I was meeting another person, but hi!",
    "Wow, you are different from last person. Hello to you!",
    "I can only handle one person at a time, else I get confused!"
]

HAPPY = [
    "Nice!",
    "Cool!",
    "Great!",
    "Wow!",
    "Superduper!",
    "Amazing!",
    "I like it!",
    "That makes my day!"
]

SORRY = [
    "Sorry!",
    "I am sorry!",
    "Forgive me!",
    "My apologies!",
    "My humble apologies!",
    "How unfortunate!"
]

GOODBYE = [
    "Bye!",
    "ByeBye",
    "Leo Lani out!",
    "See you later!",
]

AFFIRMATION = [
    " yes ",
    " yeah ",
    " correct ",
    " right ",
    " great ",
    " true ",
    " good ",
    " well done ",
    " correctamundo ",
    " splendid ",
    " indeed ",
    " superduper "
]

NEGATION = [
    " no ",
    " nope ",
    " incorrect ",
    " wrong ",
    " false ",
    " bad ",
    " stupid "
]


class MeetApp(pepper.SensorApp):

    GREET_TIMEOUT = 30
    MEET_TIMEOUT = 10
    MIN_FACE_SAMPLES = 30

    CAMERA_FREQUENCY = 4

    def __init__(self):

        people = pepper.PeopleClassifier.load_directory('leolani')
        people.update(pepper.PeopleClassifier.load_directory(EVENT))

        super(MeetApp, self).__init__(pepper.ADDRESS, people)

        self.last_greeted_name = ""
        self.last_greeted_time = 0

        self.meeting = False
        self.listening_for_name = False

        self.faces = []
        self.face_mean = np.zeros(128, np.float32)
        self.face_name = ""
        self.face_time = 0

    def begin_meeting(self):
        self.say(choice(GREETINGS))
        self.say(choice(INTRODUCE))
        self.say(choice(ASK_NAME))

        self.meeting = True
        self.listening_for_name = True
        self.face_time = time()

    def end_meeting(self):
        self.face_name = ""
        self.faces = []
        self.meeting = False

    def check_name(self, audio, hypotheses):
        name_result = self.find_names(audio, hypotheses)
        if name_result:
            name, transcript, confidence = name_result

            self.log.info(u"{}: '{}'".format(name, transcript))
            self.face_name = name
            # Verify
            self.say(choice(VERIFY_NAME).format(name))
            self.listening_for_name = False
        return name_result

    def on_utterance(self, audio):
        hypotheses = self._speech_to_text.transcribe(audio)
        if hypotheses:
            hypothesis = hypotheses[0][0].lower()

            if 'bye' in hypothesis:
                self.log.info(u"<< EXIT Conversation >>")
                self.say(choice(GOODBYE))
                sleep(5)
                self.end_meeting()
                return

            if self.meeting:
                if self.listening_for_name:
                    if not self.check_name(audio, hypotheses):
                        self.say("{} {}".format(choice(DIDNT_HEAR_NAME), choice(REPEAT_NAME)))
                else:
                    transcript, confidence = hypotheses[0]
                    self.log.info(u"{}: '{}'".format(self.face_name, transcript))

                    transcript = " {} ".format(transcript).lower()

                    for affirmation in AFFIRMATION:
                        if affirmation in transcript:

                            if len(self.faces) < self.MIN_FACE_SAMPLES:
                                self.say("{} {}".format(choice(HAPPY), choice(MORE_SAMPLES)))

                                sleep(2)
                                while len(self.faces) < self.MIN_FACE_SAMPLES:
                                    sleep(1)

                            self.say("{} {}".format(choice(HAPPY), choice(JUST_MET).format(self.face_name)))

                            self.log.info(u"Got {} Face Samples!".format(len(self.faces)))

                            # Save New Person
                            face_data = np.array(self.faces)
                            face_data.tofile(os.path.join(pepper.PeopleClassifier.ROOT, 'HPe', '{}.bin'.format(self.face_name)))
                            self._people[self.face_name] = face_data
                            self._people_classifier = pepper.PeopleClassifier(self._people)

                            self.last_greeted_name = self.face_name
                            self.last_greeted_time = time()

                            self.end_meeting()
                            return

                    for negation in NEGATION:
                        if negation in transcript:
                            self.say("{} {}".format(choice(SORRY), choice(REPEAT_NAME)))
                            self.listening_for_name = True
                            return

                    if not self.check_name(audio, hypotheses):
                        self.say("{}, {}?".format(choice(SORRY), choice(VERIFY_NAME).format(self.face_name)))
            else:
                self.log.info(u"{}: '{}'".format(self.last_greeted_name, hypothesis))

                if "let's meet" in hypothesis:
                    self.say(choice(HAPPY))
                    self.begin_meeting()
                    return

                for question, answer in QnA_STATIC.items():
                    if question.lower() in hypothesis:
                        self.say(answer)
                        return

                for question, answer_function in QnA_DYNAMIC.items():
                    if question.lower() in hypothesis.lower():
                        self.say(answer_function())
                        return

                for greeting in GREETINGS:
                    if greeting[:-1].lower() in hypothesis:
                        self.say(choice(GREETINGS))
                        return

                # Cough if she has no clue
                else:
                    self.say("ahem")

    def on_face(self, bounds, representation):
        if self.meeting:
            self.faces.append(representation)
            self.face_mean = (self.face_mean * len(self.faces) + representation) / (len(self.faces) + 1)
            self.face_time = time()

            if len(self.faces) > 2 and np.linalg.norm(self.face_mean - representation) > self.PERSON_NEW_THRESHOLD:
                self.say(choice(DIFFERENT_FACE))
                sleep(5)
                self.end_meeting()
        else:
            super(MeetApp, self).on_face(bounds, representation)

    def on_person_recognized(self, name):
        if name != self.last_greeted_name or time() - self.last_greeted_time > self.GREET_TIMEOUT:
            self.say("{}, {}! {}".format(choice(GREETINGS), name, choice(TELL_KNOWN)))
            self.last_greeted_name = name
            self.last_greeted_time = time()

    def on_person_new(self):
        if not self.meeting:
            self.begin_meeting()

    def on_camera(self, image):
        if self.meeting and time() - self.face_time > self.MEET_TIMEOUT:
            self.say(choice(LOST_FACE))
            self.end_meeting()
        super(MeetApp, self).on_camera(image)

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
    MeetApp().run()