import re
import urllib
from random import choice
from threading import Thread
from time import time, sleep

from pepper import config
from pepper.framework.abstract import AbstractApplication, AbstractIntention
from pepper.framework.component import StatisticsComponent, ObjectDetectionComponent, ContextComponent, BrainComponent, \
    FaceRecognitionComponent, SpeechRecognitionComponent, TextToSpeechComponent
from pepper.framework.sensor import UtteranceHypothesis
from pepper.knowledge import sentences, animations
from pepper.language.generation.reply import reply_to_question
from pepper.responder import *

SPEAKER_NAME_THIRD = "Her Majesty"
SPEAKER_NAME = "Your Majesty"
SPEAKER_FACE = "Her Majesty"
DEFAULT_SPEAKER = "Human"

LOCATION_NAME = "Royal Netherlands Academy of Arts and Sciences"
VU_NAME_PHONETIC = r"\\toi=lhp\\ fraiE universitai_t Amster_dam \\toi=orth\\"

IMAGE_VU = "https://www.vu.nl/nl/Images/VUlogo_NL_Wit_HR_RGB_tcm289-201376.png"
IMAGE_SELENE = "http://wordpress.let.vupr.nl/understandinglanguagebymachines/files/2019/06/7982_02_34_Selene_Orange_Unsharp_Robot_90kb.jpg"
IMAGE_LENKA = "http://wordpress.let.vupr.nl/understandinglanguagebymachines/files/2019/06/8249_Lenka_Word_Object_Reference_106kb.jpg"
IMAGE_BRAM = "http://makerobotstalk.nl/files/2018/12/41500612_1859783920753781_2612366973928996864_n.jpg"
IMAGE_PIEK = "http://www.cltl.nl/files/2019/10/8025_Classroom_Piek.jpg"

BREXIT_QUESTION = "What do you think are the implications of the Brexit for scientists?"
BREXIT_ANSWER = "Do you have a question for me?"
MIN_ANSWER_LENGTH = 4

# Override Speech Speed for added clarity!
config.NAOQI_SPEECH_SPEED = 80

RESPONDERS = [
    BrainResponder(),
    VisionResponder(), PreviousUtteranceResponder(), IdentityResponder(), LocationResponder(), TimeResponder(),
    QnAResponder(), BrexitResponder(),
    GreetingResponder(), GoodbyeResponder(), ThanksResponder(), AffirmationResponder(), NegationResponder(),
    UnknownResponder()
]


class HMKApp(AbstractApplication, StatisticsComponent,
             BrainComponent, ContextComponent,
             ObjectDetectionComponent, FaceRecognitionComponent,
             SpeechRecognitionComponent, TextToSpeechComponent):
    SUBTITLES_URL = "https://bramkraai.github.io/subtitle?text={}"

    def __init__(self, backend):
        super(HMKApp, self).__init__(backend)

        self.tablet.show(IMAGE_VU)

    def say(self, text, animation=None, block=True):
        super(HMKApp, self).say(text, animation, block)
        sleep(1.5)

    def show_text(self, text):
        text_websafe = urllib.quote(''.join([i for i in re.sub(r'\\\\\S+\\\\', "", text) if ord(i) < 128]))
        self.backend.tablet.show(self.SUBTITLES_URL.format(text_websafe))


class WaitForStartCueIntention(AbstractIntention, HMKApp):
    START_CUE_TEXT = [
        "she's here",
        "she is here",
        "the queen is here",
        "you may begin",
        "you may start",
        "you can begin",
        "you can start"
    ]

    def __init__(self, application):
        super(WaitForStartCueIntention, self).__init__(application)

        # Initialize Response Picker
        self.response_picker = ResponsePicker(self, RESPONDERS)

        # Start Chat with Default Speaker
        self.context.start_chat(DEFAULT_SPEAKER)

    def on_face(self, faces):
        # If Start Face Cue is observed by Leolani -> Start Main Intention
        if any([face.name == SPEAKER_FACE for face in faces]):
            self.say("Ah, I can see {}! Let me begin!".format(SPEAKER_NAME_THIRD))
            IntroductionIntention(self.application)

    def on_chat_turn(self, utterance):

        # If Start Text Cue is observed by Leolani -> Respond Happy & Start Main Intention
        transcript = utterance.transcript.lower()
        if any([cue in transcript for cue in self.START_CUE_TEXT]):
            self.say("Oh, {}!".format(choice(sentences.HAPPY)), animation=animations.HAPPY)
            IntroductionIntention(self.application)
            return


class IntroductionIntention(AbstractIntention, HMKApp):
    def __init__(self, application):
        super(IntroductionIntention, self).__init__(application)

        # Start Chat with Main Speaker
        self.context.start_chat(SPEAKER_NAME)

        # Start Speech
        Thread(target=self.speech).start()

    def speech(self):

        # 1.1 - Welcome
        self.say("Hello {}. Welcome to the {}. ...".format(SPEAKER_NAME, LOCATION_NAME), animations.BOW)
        self.say("We are honoured to have you here!")

        # 1.2 - Introduction
        self.say(r"I am Leolani... My name means \\vct=50\\ Voice of an Angel \\vct=100\\. in Hawaiian.", animations.I)
        self.say("I am built by students from the VU that come from all over the world. ", animations.ONCE_UPON_A_TIME)
        self.tablet.show(IMAGE_SELENE)
        self.say("Selene, from Mexico, designed my brain and thoughts!", animations.TABLET)
        self.tablet.show(IMAGE_LENKA)
        self.say("Lenka, from Serbia, taught me to understand language", animations.TABLET)
        self.tablet.show(IMAGE_BRAM)
        self.say("Bram, from the Netherlands, programmed me to perceive the world around me.", animations.TABLET)
        self.tablet.show(IMAGE_PIEK)
        self.say(
            "Peek, from the Netherlands, and I, from France and Japan, work on identity, reference and perspective in language!",
            animations.TABLET)
        self.tablet.show(IMAGE_VU)

        sleep(2.5)

        # 2.1 - Brexit Introduction
        self.say("I believe you are here to talk about the implications of the Brexit for scientists", animations.THINK)
        self.say("I am just a robot, but I have my little robot thoughts...", animations.SHY)
        self.say("The students at the VU that created me, come from all over the world... "
                 "International exchange and collaboration is key to: innovation, success, "
                 "and the spread of knowledge and democratic values... "
                 "Brexit is not helping us with this... "
                 "Europe is the beginning, the Universe is our goal... ...")

        # 2.2 - Brexit Knowledge
        self.say("As a robot, I have learned a few things about the Brexit myself!", animations.THINK)

        # 2.2.1 - Brexit in the News
        self.say("I have been reading the news lately!")
        self.say(choice(sentences.BREXIT_NEWS))
        self.say("{}!".format(choice(sentences.HAPPY)), animations.HAPPY)

        # 2.2.2 - Brexit in Brain
        self.say("I also have been talking about the Brexit with my friends!")
        self.brexit_in_brain()

        self.say("I learn a lot from my friends!")

        sleep(2.5)

        # Move to Brexit QnA
        BrexitQuestionIntention(self.application)

    def brexit_in_brain(self):
        self.answer_brain_query("what is the brexit about")
        self.answer_brain_query("what is the brexit")
        self.answer_brain_query("what is the brexit in")

    def answer_brain_query(self, query):
        try:
            question = self.context.chat.add_utterance([UtteranceHypothesis(query, 1)], False)
            question.analyze()

            brain_response = self.brain.query_brain(question)
            reply = reply_to_question(brain_response)
            if reply: self.say(reply, block=False)
        except Exception as e:
            self.log.error(e)


# 2.3 - Brexit Question
class BrexitQuestionIntention(AbstractIntention, HMKApp):
    def __init__(self, application):
        super(BrexitQuestionIntention, self).__init__(application)

        # Initialize Response Picker
        self.response_picker = ResponsePicker(self, RESPONDERS)

        self._retried = False

        # Start Chat with Speaker if not already running
        if not self.context.chatting:
            self.context.start_chat(SPEAKER_NAME)

        # Ask Brexit Question
        self.say("Oh {}, I think I have a question for you!".format(SPEAKER_NAME), animations.EXPLAIN)
        self.show_text(BREXIT_QUESTION)
        self.say(BREXIT_QUESTION)

    def on_chat_turn(self, utterance):
        responder = self.response_picker.respond(utterance)

        if self.context.chat.last_utterance.transcript.endswith("?"):
            self.say("Oops, nevermind me asking these questions. I'm just a very curious robot!", animations.ASHAMED)

        # If Pepper does not understand?
        if isinstance(responder, UnknownResponder) and len(utterance.tokens) < MIN_ANSWER_LENGTH and not self._retried:
            # -> Repeat Question
            self._retried = True
            self.say("But, {}".format(BREXIT_QUESTION))
        else:  # If a decent response can be formed
            # -> Thank Speaker and Move on to BrexitAnswerIntention
            self.say("Thank you for your answer!", animations.HAPPY)
            self.tablet.show(IMAGE_VU)
            BrexitAnswerIntention(self.application)


# 2.4 - Brexit Answer
class BrexitAnswerIntention(AbstractIntention, HMKApp):
    def __init__(self, application):
        super(BrexitAnswerIntention, self).__init__(application)

        # Initialize Response Picker
        self.response_picker = ResponsePicker(self, RESPONDERS)

        self._retried = False

        # Start Chat with Speaker if not already running
        if not self.context.chatting:
            self.context.start_chat(SPEAKER_NAME)

        self.show_text(BREXIT_ANSWER)
        self.say(BREXIT_ANSWER)

    def on_chat_turn(self, utterance):
        responder = self.response_picker.respond(utterance)

        if self.context.chat.last_utterance.transcript.endswith("?"):
            self.say("Oops, nevermind me asking these questions. I'm just a very curious robot!", animations.ASHAMED)

        # If Pepper does not understand?
        if isinstance(responder, UnknownResponder) and len(utterance.tokens) < MIN_ANSWER_LENGTH and not self._retried:
            # -> Repeat Question
            self._retried = True
            self.say("But, {}".format(BREXIT_ANSWER))
        else:  # If a decent response can be formed
            # -> Thank Speaker and Move on to OutroIntention
            self.say("Thank you!", animations.HAPPY)
            self.tablet.show(IMAGE_VU)
            OutroIntention(self.application)


class OutroIntention(AbstractIntention, HMKApp):
    def __init__(self, application):
        super(OutroIntention, self).__init__(application)

        # Initialize Response Picker
        self.response_picker = ResponsePicker(self, RESPONDERS)

        # Start Chat with Speaker if not already running
        if not self.context.chatting:
            self.context.start_chat(SPEAKER_NAME)

        Thread(target=self.speech).start()

    def speech(self):
        # 5.1 - Wish all a fruitful discussion
        self.say("I see that there are {0} people here... I wish all {0} of you a fruitful discussion!".format(
            len([obj for obj in self.context.objects if obj.name == "person"])), animations.HELLO)

        # 5.2 - Goodbye
        self.say("It's a pity the King is not here. Please say hello to him and your daughters for me.",
                 animations.FRIENDLY)
        self.say("It was nice having talked to you, {}! ... ...".format(SPEAKER_NAME), animations.BOW)

        self.say("If you have any questions, you can always ask me later!")

        sleep(4)

        self.say("I believe it is now time for a group picture! I love pictures!", animations.HAPPY)

        # Switch to Default Intention
        DefaultIntention(self.application)


class DefaultIntention(AbstractIntention, HMKApp):
    IGNORE_TIMEOUT = 60

    def __init__(self, application):
        super(DefaultIntention, self).__init__(application)

        self._ignored_people = {}
        self.response_picker = ResponsePicker(self, RESPONDERS)

    def on_chat_enter(self, name):
        self._ignored_people = {n: t for n, t in self._ignored_people.items() if time() - t < self.IGNORE_TIMEOUT}

        if name not in self._ignored_people:
            self.context.start_chat(name)
            self.say("{}, {}".format(choice(sentences.GREETING), name))

    def on_chat_exit(self):
        self.say("{}, {}".format(choice(sentences.GOODBYE), self.context.chat.speaker))
        self.context.stop_chat()

    def on_chat_turn(self, utterance):
        responder = self.response_picker.respond(utterance)

        if isinstance(responder, GoodbyeResponder):
            self._ignored_people[utterance.chat.speaker] = time()
            self.context.stop_chat()


if __name__ == '__main__':
    # Initialize Application
    application = HMKApp(config.get_backend())

    # Initialize Intention
    WaitForStartCueIntention(application)

    # Run Application
    application.run()
