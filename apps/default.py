from __future__ import unicode_literals

from pepper.framework import *
from pepper.language import *
from pepper.framework.sensor.face import FaceClassifier
from pepper import config, ApplicationBackend

from pepper.knowledge.sentences import *
from pepper.knowledge import animations

from pepper.knowledge.wikipedia import Wikipedia
from pepper.knowledge.wolfram import Wolfram
from pepper.knowledge.query import QnA

from pepper.language.utils import *

from pepper.brain.utils.helper_functions import *

import numpy as np

from random import choice
from time import time, sleep
from urllib import quote


class DefaultApp(AbstractApplication,
                 StatisticsComponent,
                 DisplayComponent,
                 BrainComponent,
                 ObjectDetectionComponent,
                 FaceDetectionComponent,
                 StreamedSpeechRecognitionComponent,
                 TextToSpeechComponent):
    pass


class IdleIntention(AbstractIntention, DefaultApp):

    GREET_TIMEOUT = 30
    BORED_TIMEOUT = 120

    PERSON_TIMEOUT = 60
    PERSONS_CHATTED_WITH = {}


    def __init__(self, application):
        super(IdleIntention, self).__init__(application)
        self._last_event = time()

    def on_face_known(self, faces):
        for face in faces:
            if time() - IdleIntention.PERSONS_CHATTED_WITH.get(face.name, 0) > IdleIntention.PERSON_TIMEOUT:
                ConversationIntention(self.application, Chat(face.name))
                break

    def on_face_new(self, faces):
        if time() - self._last_event > self.GREET_TIMEOUT:
            self.say(choice(GREETING), animations.HELLO)
            self._last_event = time()

    def on_transcript(self, hypotheses, audio):
        statement = hypotheses[0].transcript

        for meeting in ["my name is", "meet", "I am", "who are you", "what is your name", "how are you"]:
            if meeting in statement:
                MeetIntention(self.application)
                return

        for greeting in GREETING:
            if statement == greeting.lower()[:-1]:
                ConversationIntention(self.application, Chat("stranger"))
                return


class IgnoreIntention(AbstractIntention, DefaultApp):
    def on_transcript(self, hypotheses, audio):
        statement = hypotheses[0].transcript.lower()

        for wakeup in [greeting.lower()[:-1] for greeting in GREETING] + ["wake up", "pepper"]:
            if wakeup == statement:
                self.say(choice(["Ok, I'm back!", "Hello, I'm back!"]), animations.EXCITED)
                IdleIntention(self.application)
                return


class ConversationIntention(AbstractIntention, DefaultApp):

    _face_detection = None  # type: FaceDetectionComponent
    CONVERSATION_TIMEOUT = 15

    def __init__(self, application, chat):
        """
        Initialize Conversation Intention

        Parameters
        ----------
        application: DefaultApp
        chat: Chat
        """
        super(ConversationIntention, self).__init__(application)

        self._chat = chat
        self._last_seen = time()
        self._seen_objects = set()

        self._face_detection = self.require_dependency(FaceDetectionComponent)
        self._name_parser = NameParser(list(self._face_detection.face_classifier.people.keys()))

        self.say("{}, {}.".format(choice(GREETING), self.chat.speaker),
                 choice([animations.BOW, animations.FRIENDLY, animations.HI]))  # Greet Person

    @property
    def application(self):
        """
        Returns
        -------
        application: DefaultApp
        """
        return super(ConversationIntention, self).application

    @property
    def chat(self):
        return self._chat

    def say(self, text, animation=None, block=False):
        self._last_seen = time()
        super(ConversationIntention, self).say(text, animation, block)
        self._last_seen = time()

    def on_face_known(self, faces):
        if self.chat.speaker not in self._face_detection.face_classifier.people:
            self._last_seen = time()

    def on_face(self, faces):
        if self.chat.speaker not in self._face_detection.face_classifier.people:
            ConversationIntention(self.application, Chat(faces[0].name))
        if self.chat.speaker in [person.name for person in faces]:
            self._last_seen = time()

    def on_image(self, image):
        # If conversation times out, go back to idle!
        if time() - self._last_seen > self.CONVERSATION_TIMEOUT:
            self.end_conversation()

    def on_object(self, image, objects):
        # Update seen_objects with the objects seen in this frame
        self._seen_objects.update([obj.name for obj in objects])

    def on_transcript(self, hypotheses, audio):
        # Choose Utterance from Names
        utterance = self._name_parser.parse_known(hypotheses).transcript
        self.chat.add_utterance(utterance)

        self.log.info("Utterance: {}".format(utterance))

        self._last_seen = time()

        if self.respond_silence(utterance):
            return
        elif self.respond_identity(utterance):
            return
        elif self.respond_forget_me(utterance):
            return
        elif self.respond_greeting(utterance):
            return
        elif self.respond_goodbye(utterance):
            return
        elif self.respond_thanks(utterance):
            return
        elif self.respond_affirmation_negation(utterance):
            return
        elif self.respond_please_repeat_me(utterance):
            return
        elif self.respond_meeting(utterance):
            return
        elif self.respond_qna(utterance):
            return
        elif self.respond_know_object(utterance):
            return
        elif self.respond_show_page(utterance):
            return

        # Parse only sentences within bounds
        elif 3 <= len(utterance.split()) <= 10:
            if self.respond_brain(utterance):
                return
            elif self.respond_wikipedia(utterance):
                return
            elif self.respond_wolfram(utterance):
                return
            else:
                if random.uniform(0, 1) > 0.333333:
                    self.say("{}: {}, but {}!".format(
                        choice(["I think you said", "I heard", "I picked up", "I'm guessing you told me"]), utterance,
                        choice(["I don't know what it means", "I don't understand it", "I couldn't parse it",
                                "I have no idea about it", "I have no clue", "this goes above my robot-skills",
                                "I find this quite difficult to understand", "It doesn't ring any bells"])),
                        choice([animations.NOT_KNOW, animations.UNFAMILIAR, animations.UNCOMFORTABLE, animations.SHAMEFACED]))
                else:
                    self.say(choice(ELOQUENCE))

    def respond_silence(self, statement):
        for silent in ["silent", "silence", "be quiet", "relax"]:
            if silent in statement:
                self.say(choice([
                    "Ok, I'll be quiet for a bit.",
                    "Right, I'll be there when you need me!",
                    "Bye, I'm going to browse for knowledge on the display!"]),
                    animations.TIMID)
                IgnoreIntention(self.application)
                return True
        return False

    def respond_identity(self, statement):
        for ask_identity in ["who am i", "my name"]:
            if ask_identity in statement.lower():
                self.say("You are {}".format(self.chat.speaker), animations.YOU)
                return True
        return False

    def respond_forget_me(self, statement):
        for forget in ["forget", "delete", "erase", "remove", "destroy"]:
            for data in ["data", "face", "me"]:
                if forget in statement.lower() and data in statement:
                    if self.chat.speaker + ".bin" in os.listdir(config.PEOPLE_NEW_ROOT):
                        self.say("Ok {}, I will erase your data according to the EU General Data Protection Regulation!".format(self.chat.speaker), animations.FRIENDLY)
                        os.remove(os.path.join(config.PEOPLE_NEW_ROOT, self.chat.speaker + ".bin"))
                        sleep(1)
                        self.say("Boom, Done! You're still in my Random Access Memory, but as soon as I get rebooted, I will not remember you!", animations.CRAZY)
                    else:
                        self.say("Look {}, your data is already deleted!".format(self.chat.speaker), animations.AFFIRMATIVE)
                    return True
        return False

    def respond_greeting(self, statement):
        for greeting in GREETING:
            greet = re.sub('[?!.;,]', '', greeting.lower())
            for word in statement.split():
                if word.lower() == greet:
                    self.say("{}, {}!".format(choice(GREETING), self.chat.speaker), animations.HI)
                    return True
        return False

    def respond_meeting(self, statement):
        for meeting in ["let's meet"]:
            if meeting in statement:
                MeetIntention(self.application)
                return True
        return False

    def respond_goodbye(self, statement):
        for bye in GOODBYE:
            if statement.lower() == bye.lower():
                self.end_conversation()
                return True
        return False

    def respond_thanks(self, statement):
        for thank in THANK:
            thank = re.sub('[?!.;,]', '', thank.lower())

            if statement == thank:
                self.say("You are welcome, {}!".format(self.chat.speaker))
                return True
        return False

    def respond_affirmation_negation(self, statement):
        # Respond to Affirmations and Negations
        if len(statement.split(' ')) <= 3:
            for affirmation in AFFIRMATION:
                if " {} ".format(affirmation) in " {} ".format(statement.lower()):
                    self.say(choice(HAPPY), animations.HAPPY)
                    return True
            for negation in NEGATION:
                if " {} ".format(negation) in " {} ".format(statement.lower()):
                    self.say(choice(SORRY), animations.ASHAMED)
                    return True
        return False

    def respond_please_repeat_me(self, statement):
        s = statement.lower()

        if s.startswith("please repeat"):
            self.say(statement.replace("please repeat", ""))

    def respond_qna(self, question):
        answer = QnA().query(question)
        if answer:
            self.say("{} {}. {}".format(choice(ADDRESSING), self.chat.speaker, answer),
                     choice([animations.BODY_LANGUAGE, animations.EXCITED]))
        return answer

    def respond_know_object(self, question):

        SUBJECT = "leolani"
        PREDICATE = "seen"
        TAGS = ["have you ever seen ", "did you ever see "]

        for tag in TAGS:
            if tag in question.lower():
                obj = question.replace(tag, "").replace("a ", "").replace("an ", "").strip()

                print("KNOW OBJECT: ", SUBJECT, PREDICATE, obj)

                self.say("I wonder if I ever saw a {}".format(obj))

                rdf = {'subject': SUBJECT, 'predicate':PREDICATE, 'object': obj}
                template = write_template(self.chat.speaker, rdf, self.chat.id, self.chat.last_utterance.chat_turn, 'question')
                response = self.brain.query_brain(template)
                reply = reply_to_question(response,[])

                if reply:
                    self.say(reply)
                else:
                    self.say("No, I've never seen a {}".format(obj))

                return True

        return False

    def respond_show_page(self, command):
        if config.APPLICATION_BACKEND == ApplicationBackend.NAOQI:
            from pepper.framework.backend.naoqi import NaoqiTablet

            tablet = NaoqiTablet(self.backend.session)

            command = command.lower()

            if "show" in command:
                if any([src in command for src in ["github", "source", "code", "project"]]):
                    self.say("Here is our Git Hub page!", animations.TABLET)
                    tablet.show("https://github.com/cltl/pepper")
                    return True
                if any([src in command for src in ["page", "docs", "documentation"]]):
                    self.say("Here is the documentation of our project!", animations.TABLET)
                    tablet.show("https://cltl.github.io/pepper")
                    return True
                if "google" in command:
                    self.say("I'll let you Google!")
                    tablet.show("https://google.com")
                    return True
                if "open images" in command:
                    self.say("I'll show you the Open Images Dataset", animations.TABLET)
                    tablet.show("https://storage.googleapis.com/openimages/display/visualizer/index.html")
                    return True
                if "show me images of " in command:
                    target = command.replace("show me images of ", "")
                    self.say("I'll show you images of {}".format(target), animations.TABLET)
                    tablet.show("https://www.google.com/search?tbm=isch&q={}".format(quote(target)))
                    return True

            elif "hide" in command:
                self.say("Ok, I'll do that!", animations.TABLET)
                tablet.hide()
                return True
        return False

    def respond_brain(self, question):
        try:
            objects = list(self._seen_objects)

            expression = classify_and_process_utterance(
                question, self.chat.speaker, self.chat.id, self.chat.last_utterance.chat_turn, objects)

            # TODO new_response = language.get_template(self.chat,self.chat.last_utterance, self.application.brain)

            # Cancel if not a valid expression
            if not expression or 'utterance_type' not in expression:
                return False

            # Process Questions
            elif expression['utterance_type'] == 'question':
                result = self.application.brain.query_brain(expression)
                response = reply_to_question(result, objects)

                if response:
                    self.say(response.replace('_', ' '), choice([animations.BODY_LANGUAGE, animations.EXCITED]))
                    return True
                else:
                    # self.say("{}, but {}!".format(
                    #     choice(["I don't know", "I haven't heard it before", "I have know idea about it"]),
                    #     choice(["I'll look it up online", "let me search the web", "I will check my internet sources"]),
                    #     animations.THINK
                    # ))
                    return False

            # Process Statements
            elif expression['utterance_type'] == 'statement':
                result = self.application.brain.update(expression)
                # response = reply_to_statement(result, self.chat.speaker, objects, self)
                response = phrase_update(result, True, True)
                self.say(response.replace('_', ' '), animations.EXCITED)

            return True
        except: pass
        return False

    def respond_wikipedia(self, question):
        result = Wikipedia().query(question)
        if result:
            answer, url = result

            answer = re.split('[.\n]', answer)[0]

            self.say("{}, {}, {}.".format(choice(ADDRESSING), choice(USED_WWW), self.chat.speaker), animations.CLOUD)

            tablet = None
            if config.APPLICATION_BACKEND == ApplicationBackend.NAOQI:
                from pepper.framework.backend.naoqi import NaoqiTablet
                tablet = NaoqiTablet(self.backend.session)
                tablet.show(url)

            self.say(answer, animations.EXPLAIN, block=True)

            if tablet:
                tablet.hide()

        return result

    def respond_wolfram(self, question):
        answer = Wolfram().query(question)
        if answer:
            self.say("{}, {}, {}.".format(choice(ADDRESSING), choice(USED_WWW), self.chat.speaker), animations.CLOUD)
            self.say(answer, animations.EXPLAIN)
        return answer

    def end_conversation(self):
        self.say("{}, {}!".format(
            choice(["See you later", "ByeBye", "Till another time", "It was good having talked to you", "Goodbye"]),
            self.chat.speaker), animations.BOW)

        IdleIntention.PERSONS_CHATTED_WITH[self.chat.speaker] = time()

        IdleIntention(self.application)


class MeetIntention(AbstractIntention, DefaultApp):

    MEET_TIMEOUT = 30
    UTTERANCE_TIMEOUT = 15

    MIN_SAMPLES = 30
    NAME_CONFIDENCE = 0.8

    _face_detection = None  # type: FaceDetectionComponent

    def __init__(self, application):
        super(MeetIntention, self).__init__(application)

        self._face_detection = self.require_dependency(FaceDetectionComponent)
        self._name_parser = NameParser(list(self._face_detection.face_classifier.people.keys()))

        self._last_seen = time()
        self._last_utterance = time()

        self._name = ""
        self._face = []

        self.say("{}, {}".format(choice(GREETING), choice(INTRODUCE)))
        self.say(choice(ASK_NAME))

        # for sentence in [
        #         "I wish to meet you!",
        #         "By continuing to meet me, you agree with locally storing your face features and name.",
        #         "Your personal data is only used for the purpose of meeting you and not shared with third parties.",
        #         "After meeting, you can always ask me to erase your personal data, no hard feelings!",
        #         "Ok, enough legal stuff! {}".format(choice(ASK_NAME))]:
        #
        #     self.say(sentence)
        #     self._last_utterance = time()
        #     sleep(0.25)

    def on_image(self, image):
        # If meeting times out, go back to idle!
        if time() - self._last_seen > self.MEET_TIMEOUT:
            self.end_conversation()

        # If silence was observed, ask away!
        if time() - self._last_utterance > self.UTTERANCE_TIMEOUT:
            self._last_utterance = time()
            if self._name:
                self.say("{} {}".format(choice(UNDERSTAND), choice(VERIFY_NAME).format(self._name)), animations.YOUR)
            else:
                self.say("{} {}".format(choice(DIDNT_HEAR_NAME), choice(REPEAT_NAME)), animations.UNKNOWN)

    def on_face(self, faces):
        self._face.append(faces[0].representation)
        self._last_seen = time()

    def on_transcript(self, hypotheses, audio):
        self._last_utterance = time()

        utterance = hypotheses[0].transcript

        if self.goodbye(utterance):
            self.say(choice(["See you later", "ByeBye", "Till another time",
                             "It was good having talked to you", "Goodbye"]), animations.BOW)
            IdleIntention(self.application)
            return

        # If name is heard and affirmation is given by new person
        if self._name and self.is_affirmation(utterance):

            # If not enough face samples have been gathered, gather more!
            if len(self._face) < self.MIN_SAMPLES:
                self.say("{} {}".format(choice(JUST_MET).format(self._name), choice(MORE_FACE_SAMPLES)), animations.FRIENDLY)
                while len(self._face) < self.MIN_SAMPLES:
                    self._last_utterance = time()
                    sleep(1)
                self.say(choice(THANK), animations.HAPPY)

            # Save person to Disk
            self.save_person()
            self.say("{} {}".format(choice(HAPPY), choice(JUST_MET).format(self._name)), animations.HI)

            # Start Conversation with New Person
            ConversationIntention(self.application, Chat(self._name))

        else:  # Try to parse name
            self.say(choice(THINKING), animations.THINK)

            # Parse Name
            parsed_name = self._name_parser.parse_new(audio)
            if parsed_name and parsed_name[0] > self.NAME_CONFIDENCE:
                self._name, confidence = parsed_name
                self.say("{} {}".format(choice(UNDERSTAND), choice(VERIFY_NAME).format(self._name)), animations.FRIENDLY)
            elif self.is_negation(utterance):
                self.say("{} {}".format(choice(SORRY), choice(REPEAT_NAME)), animations.ASHAMED)
            else:
                self.say("{} {}".format(choice(DIDNT_HEAR_NAME), choice(REPEAT_NAME)), animations.ASHAMED)

    @staticmethod
    def is_affirmation(statement):
        for word in statement.split():
            if word in AFFIRMATION:
                return True
        return False

    @staticmethod
    def is_negation(statement):
        for word in statement.split():
            if word in NEGATION:
                return True
        return False

    @staticmethod
    def goodbye(statement):
        for bye in GOODBYE:
            if statement.lower() == re.sub('[?!.;,]', '', bye.lower()):
                return True
        return False

    def end_conversation(self):
        self.say("{}!".format(
            choice(["See you later", "ByeBye", "Till another time", "It was good having talked to you", "Goodbye"])), animations.BOW)
        IdleIntention(self.application)

    def save_person(self):
        people = self._face_detection.face_classifier.people
        name = self._name

        if name in people:
            name_index = 2
            while name in people:
                name = "{}{}".format(self._name, name_index)
                name_index += 1

        people[str(self._name)] = self._face
        self._face_detection.face_classifier = FaceClassifier(people)
        np.concatenate(self._face).tofile(os.path.join(config.PEOPLE_NEW_ROOT, "{}.bin".format(name)))


if __name__ == '__main__':
    app = DefaultApp(config.get_backend())
    IdleIntention(app)
    app.run()
