from pepper.framework import *
from pepper.responder import *
from pepper.knowledge import sentences, animations
from pepper.language import Utterance
from pepper.language.generation.reply import reply_to_question
from pepper import config

from threading import Thread
from random import choice
from time import time

SPEAKER_NAME_THIRD = "Dear guest"
SPEAKER_NAME = "Dear guest"
SPEAKER_FACE = "HUMAN"
DEFAULT_SPEAKER = "Human"
TOPIC_NAME = "Master Information Day"

TOPIC_ROBOT_THOUGHT = "A future where humans and robots work together is not too far from now. Masters degrees that give the skills for this future will be very valuable."

LOCATION_NAME = "The main building at the VU"
VU_NAME_PHONETIC = r"\\toi=lhp\\ fraiE universitai_t Amster_dam \\toi=orth\\"

IMAGE_VU = "https://www.vu.nl/nl/Images/VUlogo_NL_Wit_HR_RGB_tcm289-201376.png"
IMAGE_SELENE = "http://wordpress.let.vupr.nl/understandinglanguagebymachines/files/2019/06/7982_02_34_Selene_Orange_Unsharp_Robot_90kb.jpg"
IMAGE_LENKA = "http://wordpress.let.vupr.nl/understandinglanguagebymachines/files/2019/06/8249_Lenka_Word_Object_Reference_106kb.jpg"
IMAGE_BRAM = "http://makerobotstalk.nl/files/2018/12/41500612_1859783920753781_2612366973928996864_n.jpg"
IMAGE_LEA = "http://www.cltl.nl/files/2020/03/Lea.jpg"
IMAGE_PIEK = "http://www.cltl.nl/files/2019/10/8025_Classroom_Piek.jpg"
IMAGE_NLP = "https://miro.medium.com/max/1000/1*CtR2lIHDkhB9M8Jt4irSyg.gif"

TOPIC_QUERY = "Masters degrees"
TOPIC_QUESTION = "What master programme are you interested in?"
TOPIC_ANSWER = "Do you have a question for me?"
MIN_ANSWER_LENGTH = 4

# Override Speech Speed for added clarity!
config.NAOQI_SPEECH_SPEED = 90

RESPONDERS = [
    BrainResponder(),
    VisionResponder(), PreviousUtteranceResponder(), IdentityResponder(), LocationResponder(), TimeResponder(),
    QnAResponder(),
    GreetingResponder(), GoodbyeResponder(), ThanksResponder(), AffirmationResponder(), NegationResponder(),
    UnknownResponder()
]


class PresentTeamApp(AbstractApplication, StatisticsComponent,
                     SubtitlesComponent,
                     BrainComponent, ContextComponent,
                     ObjectDetectionComponent, FaceRecognitionComponent,
                     SpeechRecognitionComponent, TextToSpeechComponent):
    SUBTITLES_URL = "https://bramkraai.github.io/subtitle?text={}"

    def __init__(self, backend):
        super(PresentTeamApp, self).__init__(backend)

        self.tablet.show(IMAGE_VU)

    def say(self, text, animation=None, block=True):
        super(PresentTeamApp, self).say(text, animation, block)
        sleep(1.5)

    def show_text(self, text):
        self.backend.tablet.show(self.SUBTITLES_URL.format(text))


class WaitForStartCueIntention(AbstractIntention, PresentTeamApp):
    START_CUE_TEXT = [
        "hello",
        "hallo",
        "hi",
        "morning",
        "evening",
        "afternoon",
        "hoi",
        "who are you",
        "a guest arrived",
        "you may begin",
        "you may start",
        "you can begin",
        "you can start",
        "robot"
    ]

    GREET_TIMEOUT = 15  # Only Greet people once every X seconds

    def __init__(self, application):
        """Greets New and Known People"""
        self.name_time = {}  # Dictionary of <name, time> pairs, to keep track of who is greeted when

        super(WaitForStartCueIntention, self).__init__(application)

        # Initialize Response Picker
        self.response_picker = ResponsePicker(self, RESPONDERS)

        # Start Chat with Default Speaker
        self.context.start_chat(DEFAULT_SPEAKER)

    def on_face_known(self, faces):
        """
        On Person Event.
        Called every time a known face is detected.
        """
        for person in faces:
            if self.is_greeting_appropriate(person.name):
                self.say("Hello, {}!".format(person.name))

    def on_face_new(self, faces):
        """
        On New Person Event.
        Called every time an unknown face is detected.
        """

        if self.is_greeting_appropriate("new"):
            self.say("I see a new person!, Hello stranger!")

    def is_greeting_appropriate(self, name):
        """Returns True if greeting is appropriate and updates Greeting Time"""

        # Appropriateness arises when
        #  1. person hasn't been seen before, or
        #  2. enough time has passed since last sighting
        if name not in self.name_time or (time() - self.name_time[name]) > self.GREET_TIMEOUT:
            # Store last seen time (right now) in name_time dictionary
            self.name_time[name] = time()

            # Return "Appropriate"
            return True

        # Return "Not Appropriate"
        return False

    def on_face(self, faces):
        # If Start Face Cue is observed by Leolani -> Start Main Intention
        if self.is_greeting_appropriate("new"):
            self.say("I see a new person!, Hello stranger!")
            IntroductionIntention(self.application)

        # Before was like this
        if any([self.on_face_new(face) for face in faces]):
            self.say("Ah, I can see {}! Let me begin!".format(SPEAKER_NAME_THIRD))
            IntroductionIntention(self.application)

        # Changed to this
        if len(faces) == 0:
            self.say("Ah, I can see {}! Let me begin!".format(SPEAKER_NAME_THIRD))
            IntroductionIntention(self.application)

    def on_chat_turn(self, utterance):

        # If Start Text Cue is observed by Leolani -> Respond Happy & Start Main Intention
        transcript = utterance.transcript.lower()
        if any([cue in transcript for cue in self.START_CUE_TEXT]):
            self.say("Oh, {}!".format(choice(sentences.HAPPY)), animation=animations.HAPPY)
            IntroductionIntention(self.application)
            return


class IntroductionIntention(AbstractIntention, PresentTeamApp):
    def __init__(self, application):
        super(IntroductionIntention, self).__init__(application)

        # Start Chat with Main Speaker
        self.context.start_chat(SPEAKER_NAME)

        # Start Speech
        Thread(target=self.speech).start()

    def speech(self):

        # 1.1 - Welcome
        self.say("Hello {}. Welcome to the {}. ...".format(SPEAKER_NAME, LOCATION_NAME), animations.BOW)
        self.say("My apologies is I am slow today, my internet connection is not very good")
        self.say("We are thrilled to have you here!")

        # 1.2 - Introduction
        self.say(r"I am lio-lawhni... My name means \\vct=50\\ Voice of an Angel \\vct=100\\. in Hawaiian.",
                 animations.I)
        self.say("I am built by students from the VU that come from all over the world. ", animations.ONCE_UPON_A_TIME)
        self.tablet.show(IMAGE_SELENE)
        sleep(1.0)
        self.say("Selene, from Mexico, designed my brain and thoughts!", animations.TABLET)
        self.tablet.show(IMAGE_LENKA)
        sleep(1.0)
        self.say("Lenka, from Serbia, taught me to understand language", animations.TABLET)
        self.tablet.show(IMAGE_BRAM)
        sleep(1.0)
        self.say("Bram, from the Netherlands, programmed me to perceive the world around me.", animations.TABLET)
        self.tablet.show(IMAGE_LEA)
        sleep(1.0)
        self.say("Lea, from Germany, has recently joined the team and will help me improve my language understanding.",
                 animations.TABLET)
        self.tablet.show(IMAGE_PIEK)
        sleep(1.0)
        self.say(
            "Peek, from the Netherlands, and I, from France and Japan, work on identity, reference and perspective in language!",
            animations.TABLET)
        self.tablet.show(IMAGE_VU)

        sleep(2.5)

        # 2.1 - Topic Introduction
        self.say("I believe you are here for " + TOPIC_NAME, animations.THINK)
        self.say("Here at the {} there are many interesting programs to choose from! ".format(VU_NAME_PHONETIC),
                 animations.ENTHUSIASTIC)
        self.say("I am just a robot, but I have my little robot thoughts...", animations.SHY)
        self.say(TOPIC_ROBOT_THOUGHT)

        # 2.2 - Topic Knowledge
        self.say("As a robot, I have learned a few things about " + TOPIC_QUERY + " myself!", animations.THINK)
        self.say("For example, the Linguistics Department here offers a specialized program on Text Mining ",
                 animations.JOYFUL)

        # 2.2.1 - Topic in the News
        self.say("{}".format(choice(sentences.USED_WWW)))
        self.say(choice(sentences.FUN_NLP_FACTS))
        self.tablet.show(IMAGE_NLP)
        sleep(5.0)
        self.say("Impressive, right?".format(choice(sentences.HAPPY)), animations.EXCITED)

        # 2.2.2 - Topic in Brain
        self.say("I also have been talking about " + TOPIC_NAME + " with my friends!")
        self.topic_in_brain()

        self.say("I learn a lot from my friends!")

        sleep(2.5)

        # Move to Topic QnA
        TopicQuestionIntention(self.application)

    def topic_in_brain(self):
        self.answer_brain_query("what is " + TOPIC_QUERY + " ")

    def answer_brain_query(self, query):
        try:
            question = self.context.chat.add_utterance([UtteranceHypothesis(query, 1)], False)
            question.analyze()

            brain_response = self.brain.query_brain(question)
            reply = reply_to_question(brain_response)
            if reply: self.say(reply, block=False)
        except Exception as e:
            self.log.error(e)


# 2.3 - Topic Question
class TopicQuestionIntention(AbstractIntention, PresentTeamApp):
    def __init__(self, application):
        super(TopicQuestionIntention, self).__init__(application)

        # Initialize Response Picker
        self.response_picker = ResponsePicker(self, RESPONDERS)

        self._retried = False

        # Start Chat with Speaker if not already running
        if not self.context.chatting:
            self.context.start_chat(SPEAKER_NAME)

        # Ask Topic Question
        self.say("Oh {}, I think I have a question for you!".format(SPEAKER_NAME), animations.EXPLAIN)
        self.show_text(TOPIC_QUESTION)
        self.say(TOPIC_QUESTION)

    def on_chat_turn(self, utterance):
        responder = self.response_picker.respond(utterance)

        if self.context.chat.last_utterance.transcript.endswith("?"):
            self.say("Oops, nevermind me asking these questions. I'm just a very curious robot!", animations.ASHAMED)

        # If Pepper does not understand?
        if isinstance(responder, UnknownResponder) and len(utterance.tokens) < MIN_ANSWER_LENGTH and not self._retried:
            # -> Repeat Question
            self._retried = True
            self.say("But, {}".format(TOPIC_QUESTION))
        else:  # If a decent response can be formed
            # -> Thank Speaker and Move on to TopicAnswerIntention
            self.say("That sounds interesting! I wish you the best of luck", animations.HAPPY)
            self.tablet.show(IMAGE_VU)
            TopicAnswerIntention(self.application)


# 2.4 - Topic Answer
class TopicAnswerIntention(AbstractIntention, PresentTeamApp):
    def __init__(self, application):
        super(TopicAnswerIntention, self).__init__(application)

        # Initialize Response Picker
        self.response_picker = ResponsePicker(self, RESPONDERS)

        self._retried = False

        # Start Chat with Speaker if not already running
        if not self.context.chatting:
            self.context.start_chat(SPEAKER_NAME)

        self.show_text(TOPIC_ANSWER)
        self.say(TOPIC_ANSWER)

    def on_chat_turn(self, utterance):
        responder = self.response_picker.respond(utterance)

        if self.context.chat.last_utterance.transcript.endswith("?"):
            self.say("Oops, nevermind me asking these questions. I'm just a very curious robot!", animations.ASHAMED)

        # If Pepper does not understand?
        if isinstance(responder, UnknownResponder) and len(utterance.tokens) < MIN_ANSWER_LENGTH and not self._retried:
            # -> Repeat Question
            self._retried = True
            self.say("But, {}".format(TOPIC_ANSWER))
        else:  # If a decent response can be formed
            # -> Thank Speaker and Move on to OutroIntention
            self.say("Thank you!", animations.HAPPY)
            self.tablet.show(IMAGE_VU)
            OutroIntention(self.application)


class OutroIntention(AbstractIntention, PresentTeamApp):
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
        self.say("It's a pity we could not talk more and get to know each other.",
                 animations.FRIENDLY)
        self.say("It was nice having talked to you, {}! ... ...".format(SPEAKER_NAME), animations.BOW)

        self.say("If you have any questions, you can always ask me later!")

        sleep(4)

        self.say("You may make a selfie with me! I love pictures!", animations.HAPPY)

        # Switch to Default Intention
        DefaultIntention(self.application)


class DefaultIntention(AbstractIntention, PresentTeamApp):
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

    def on_face(self, faces):
        self.say("Ah, I can see someone! Let me begin!")
        WaitForStartCueIntention(self.application)


if __name__ == '__main__':
    # Initialize Application
    application = PresentTeamApp(config.get_backend())

    # Initialize Intention
    WaitForStartCueIntention(application)

    # Run Application
    application.run()
