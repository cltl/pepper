from __future__ import unicode_literals

from pepper.framework import *
from pepper.language import *
from pepper.sensor.face import FaceClassifier
from pepper import config

from pepper.knowledge.sentences import *

from pepper.knowledge.wikipedia import Wikipedia
from pepper.knowledge.wolfram import Wolfram
from pepper.knowledge.query import QnA

import numpy as np

from random import choice
from time import time, sleep


class DefaultApp(Application, VideoDisplay, Statistics, ObjectDetection, FaceDetection, SpeechRecognition):
    pass


class IdleIntention(Intention, FaceDetection, SpeechRecognition):
    def on_person(self, persons):
        ConversationIntention(self.application, Chat(persons[0].name))

    def on_new_person(self, persons):
        pass
        # MeetIntention(self.application)

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


class IgnoreIntention(Intention, SpeechRecognition):
    def on_transcript(self, hypotheses, audio):
        statement = hypotheses[0].transcript.lower()

        for wakeup in [greeting.lower()[:-1] for greeting in GREETING] + ["wake up", "pepper"]:
            if wakeup == statement:
                self.say(choice(["Ok, I'm back!", "Hello, I'm back!"]))
                IdleIntention(self.application)
                return


class ConversationIntention(Intention, ObjectDetection, FaceDetection, SpeechRecognition):

    _face_detection = None  # type: FaceDetection
    CONVERSATION_TIMEOUT = 15

    def __init__(self, application, chat):
        """
        Initialize Conversation Intention

        Parameters
        ----------
        application: Application
        chat: Chat
        """
        super(ConversationIntention, self).__init__(application)

        self._chat = chat
        self._last_seen = time()
        self._seen_objects = set()

        self._face_detection = self.require_dependency(FaceDetection)
        self._name_parser = NameParser(list(self._face_detection.face_classifier.people.keys()))

        self.say("{}, {}.".format(choice(GREETING), self.chat.speaker))  # Greet Person

    @property
    def chat(self):
        return self._chat

    def say(self, text):
        self._last_seen = time()
        super(ConversationIntention, self).say(text)
        self._last_seen = time()

    def on_face(self, faces):
        if self.chat.speaker not in self._face_detection.face_classifier.people:
            self._last_seen = time()

    def on_person(self, persons):
        if self.chat.speaker not in self._face_detection.face_classifier.people:
            ConversationIntention(self.application, Chat(persons[0].name))
        if self.chat.speaker in [person.name for person in persons]:
            self._last_seen = time()

    def on_image(self, image):
        # If conversation times out, go back to idle!
        if time() - self._last_seen > self.CONVERSATION_TIMEOUT:
            self.end_conversation()

    def on_object(self, image, objects):
        # Update seen_objects with the objects seen in this frame
        self._seen_objects.update([obj.name for obj in objects])

    def on_transcript(self, hypotheses, audio):
        # Process Utterance
        utterance = hypotheses[0].transcript
        self.chat.add_utterance(utterance)

        self._last_seen = time()

        if self.respond_silence(utterance):
            return
        elif self.respond_forget_me(utterance):
            return
        elif self.respond_greeting(utterance):
            return
        elif self.respond_goodbye(utterance):
            return
        elif self.respond_affirmation_negation(utterance):
            return
        elif self.respond_please_repeat_me(utterance):
            return
        elif self.respond_meeting(utterance):
            return
        elif self.respond_qna(utterance):
            return

        # Parse only sentences within bounds
        elif 3 <= len(utterance.split()) <= 10:

            # Parse Names
            utterance = self._name_parser.parse_known(hypotheses).transcript

            self.say(choice(THINKING))

            if self.respond_brain(utterance):
                return
            elif self.respond_wikipedia(utterance):
                return
            elif self.respond_wolfram(utterance):
                return
            else:
                self.say("{}: {}, but {}!".format(
                    choice(["I think you said", "I heard", "I picked up", "I'm guessing you told me"]), utterance,
                    choice(["I don't know what it means", "I don't understand it", "I couldn't parse it",
                            "I have no idea about it", "I have no clue", "this goes above my robot-skills",
                            "I find this quite difficult to understand", "It doesn't ring any bells"])))

    def respond_silence(self, statement):
        for silent in ["silent", "silence", "be quiet", "relax"]:
            if silent in statement:
                self.say(choice(["Ok, I'll be quiet for a bit.", "Right, I'll be there when you need me!", "Bye, I'm going to browse for knowledge on the web!"]))
                IgnoreIntention(self.application)
                return True
        return False

    def respond_forget_me(self, statement):
        for forget in ["forget", "delete", "erase"]:
            for data in ["data", "face", "me"]:
                if forget in statement.lower() and data in statement:
                    if self.chat.speaker + ".bin" in os.listdir(config.NEW_FACE_DIRECTORY):
                        self.say("Ok {}, I will erase your data according to the EU General Data Protection Regulation!".format(self.chat.speaker))
                        os.remove(os.path.join(config.NEW_FACE_DIRECTORY, self.chat.speaker + ".bin"))
                    else:
                        self.say("Look {}, your data is already deleted!".format(self.chat.speaker))


                    return True
        return False

    def respond_greeting(self, statement):
        for greeting in GREETING:
            greet = re.sub('[?!.;,]', '', greeting.lower())
            for word in statement.split():
                if word.lower() == greet:
                    self.say("{}, {}!".format(choice(GREETING), self.chat.speaker))
                    return True
        return False

    def respond_meeting(self, statement):
        for meeting in ["my name is", "let's meet", "I am"]:
            if meeting in statement:
                MeetIntention(self.application)
                return True
        return False

    def respond_goodbye(self, statement):
        for bye in GOODBYE:
            if statement == re.sub('[?!.;,]', '', bye.lower()):
                self.end_conversation()
                return True
        return False

    def respond_affirmation_negation(self, statement):
        # Respond to Affirmations and Negations
        if len(statement.split(' ')) <= 3:
            for affirmation in AFFIRMATION:
                if " {} ".format(affirmation) in " {} ".format(statement.lower()):
                    self.say(choice(HAPPY))
                    return True
            for negation in NEGATION:
                if " {} ".format(negation) in " {} ".format(statement.lower()):
                    self.say(choice(SORRY))
                    return True
        return False

    def respond_please_repeat_me(self, statement):
        s = statement.lower()

        if s.startswith("please repeat"):
            self.say(statement.replace("please repeat", ""))

    def respond_qna(self, question):
        answer = QnA().query(question)
        if answer:
            self.say("{} {}. {}".format(choice(ADDRESSING), self.chat.speaker, answer))
        return answer

    def respond_brain(self, question):
        try:
            objects = list(self._seen_objects)

            expression = classify_and_process_utterance(
                question, self.chat.speaker, self.chat.id, self.chat.last_utterance.utterance_id.chat_turn, objects)

            # Cancel if not a valid expression
            if not expression or 'utterance_type' not in expression:
                return False

            # Process Questions
            elif expression['utterance_type'] == 'question':
                result = self.application.brain.query_brain(expression)
                response = reply_to_question(result, objects)

                if response:
                    self.say(response.replace('_', ' '))
                    return True
                else:
                    self.say("{}, but {}!".format(
                        choice(["I don't know", "I haven't heard it before", "I have know idea about it"]),
                        choice(["I'll look it up online", "let me search the web", "I will check my internet sources"])
                    ))
                    return False

            # Process Statements
            elif expression['utterance_type'] == 'statement':
                result = self.application.brain.update(expression)
                response = reply_to_statement(result, self.chat.speaker, objects, self)
                self.say(response.replace('_', ' '))

            return True

        except Exception as e:
            self.log.error("NLP ERROR: {}".format(e))
            return False

    def respond_wikipedia(self, question):
        answer = Wikipedia().nlp_query(question)
        if answer:
            answer = answer.split('. ')[0]
            self.say("{}, {}, {}. {}".format(choice(ADDRESSING), choice(USED_WWW), self.chat.speaker, answer))
        return answer

    def respond_wolfram(self, question):
        answer = Wolfram().query(question)
        if answer:
            self.say("{}, {}, {}. {}".format(choice(ADDRESSING), choice(USED_WWW), self.chat.speaker, answer))
        return answer

    def end_conversation(self):
        self.say("{}, {}!".format(
            choice(["See you later", "ByeBye", "Till another time", "It was good having talked to you", "Goodbye"]),
            self.chat.speaker))
        IdleIntention(self.application)


class MeetIntention(Intention, ObjectDetection, FaceDetection, SpeechRecognition):

    MEET_TIMEOUT = 30
    UTTERANCE_TIMEOUT = 15

    MIN_SAMPLES = 30
    NAME_CONFIDENCE = 0.8

    _face_detection = None  # type: FaceDetection

    def __init__(self, application):
        super(MeetIntention, self).__init__(application)

        self._face_detection = self.require_dependency(FaceDetection)
        self._name_parser = NameParser(list(self._face_detection.face_classifier.people.keys()))

        self._last_seen = time()
        self._last_utterance = time()

        self._name = ""
        self._face = []

        self.say("{} {} {}".format(choice(GREETING), choice(INTRODUCE), choice(ASK_NAME)))

    def on_image(self, image):
        # If meeting times out, go back to idle!
        if time() - self._last_seen > self.MEET_TIMEOUT:
            self.end_conversation()

        # If silence was observed, ask away!
        if time() - self._last_utterance > self.UTTERANCE_TIMEOUT:
            self._last_utterance = time()
            if self._name:
                self.say("{} {}".format(choice(UNDERSTAND), choice(VERIFY_NAME).format(self._name)))
            else:
                self.say("{} {}".format(choice(DIDNT_HEAR_NAME), choice(REPEAT_NAME)))

    def on_face(self, faces):
        self._face.append(faces[0].representation)
        self._last_seen = time()

    def on_transcript(self, hypotheses, audio):
        self._last_utterance = time()

        utterance = hypotheses[0].transcript

        if self.goodbye(utterance):
            self.say(choice(["See you later", "ByeBye", "Till another time",
                             "It was good having talked to you", "Goodbye"]))
            IdleIntention(self.application)
            return

        # If name is heard and affirmation is given by new person
        if self._name and self.is_affirmation(utterance):

            # If not enough face samples have been gathered, gather more!
            if len(self._face) < self.MIN_SAMPLES:
                self.say("{} {}".format(choice(JUST_MET).format(self._name), choice(MORE_FACE_SAMPLES)))
                while len(self._face) < self.MIN_SAMPLES:
                    self._last_utterance = time()
                    sleep(1)
                self.say(choice(THANK))

            # Save person to Disk
            self.save_person()
            self.say("{} {}".format(choice(HAPPY), choice(JUST_MET).format(self._name)))

            # Start Conversation with New Person
            ConversationIntention(self.application, Chat(self._name))

        else:  # Try to parse name
            self.say(choice(THINKING))

            # Parse Name
            parsed_name = self._name_parser.parse_new(audio)
            if parsed_name and parsed_name[0] > self.NAME_CONFIDENCE:
                self._name, confidence = parsed_name
                self.say("{} {}".format(choice(UNDERSTAND), choice(VERIFY_NAME).format(self._name)))
            elif self.is_negation(utterance):
                self.say("{} {}".format(choice(SORRY), choice(REPEAT_NAME)))
            else:
                self.say("{} {}".format(choice(DIDNT_HEAR_NAME), choice(REPEAT_NAME)))

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
            if statement == re.sub('[?!.;,]', '', bye.lower()):
                return True
        return False

    def end_conversation(self):
        self.say("{}!".format(
            choice(["See you later", "ByeBye", "Till another time", "It was good having talked to you", "Goodbye"])))
        IdleIntention(self.application)

    def save_person(self):
        people = self._face_detection.face_classifier.people

        if self._name not in people:
            people[str(self._name)] = self._face
            self._face_detection.face_classifier = FaceClassifier(people)

        np.concatenate(self._face).tofile(os.path.join(config.NEW_FACE_DIRECTORY, "{}.bin".format(self._name)))


if __name__ == '__main__':
    app = DefaultApp(config.get_backend())
    IdleIntention(app)
    app.run()
