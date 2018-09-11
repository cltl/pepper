from pepper.framework.system import SystemApp
from pepper.framework.naoqi import NaoqiApp
from pepper import config

from pepper.framework import AbstractIntention
from pepper.language import *
from pepper.language.names import NameParser

from pepper.knowledge.wolfram import Wolfram
from pepper.knowledge.query import QnA

from pepper.intention.meet import MeetIntention

from pepper.knowledge.sentences import *
from random import getrandbits, choice


class ReactiveIntention(AbstractIntention):
    def __init__(self, app):
        super(ReactiveIntention, self).__init__(app)

        # The name parser is used to name-correct Google Speech outputs
        self._name_parser = NameParser(list(self.app._faces.keys()))

        # Speaker and Conversation info
        self._speaker = "human"
        self._chat_id = None
        self._chat_turn = 0

        # Set of Objects seen (passed to NLP as a list)
        self._objects = set()

    def on_face_new(self, bounds, face):
        self.initiate_conversation("human")

    def on_face_known(self, bounds, face, name):
        self.initiate_conversation(name)

    def initiate_conversation(self, name):
        if name != self._speaker:  # If person switches

            # Initiate Conversation
            self._speaker = name
            self._chat_id = getrandbits(128)
            self._chat_turn = 0
            self.log.info("Initiated Conversation with {}".format(self._speaker))

            # Greet Person
            self.say("{} {}. {}".format(choice(GREETING), name, choice(TELL_KNOWN)))

            # Tell Person about random seen object
            if self._objects:
                self.say(choice(TELL_OBJECT).format(choice(list(self._objects))))

    def on_object(self, image, objects):
        new_objects = []

        # Loop through currently visible objects, which are defined as (<name>, <confidence>, <bounding box>)
        for obj, confidence, bbox in objects:

            # if new object is not yet seen, mention it and add it to seen objects
            if obj not in self._objects:
                new_objects.append((obj, confidence))
                self._objects.add(obj)

        # Tell about seen objects and add them to seen objects
        if new_objects:
            self._tell_objects(new_objects)

    def on_transcript(self, transcript, audio):
        if self._speaker:  # If Speaker is Recognized
            question = transcript[0][0]

            # Try to answer simple QnA
            answer = QnA().query(question)
            if answer:
                self.say("{} {}. {}".format(choice(ADDRESSING), self._speaker, answer))
                return

            # Parse Names in Utterance
            utterance, confidence = self._name_parser.parse_known(transcript)

            # Parse Expression
            expression = classify_and_process_utterance(
                utterance, self._speaker, self._chat_id, self._chat_turn, list(self._objects))
            self._chat_turn += 1

            # Cancel if not a valid expression
            if not expression or not 'utterance_type' in expression:

                # Try Wolfram
                answer = Wolfram().query(question)
                if answer:
                    self.say("{} {}. {}".format(choice(ADDRESSING), self._speaker, answer))
                else:
                    for affirmation in AFFIRMATION:
                        if " {} ".format(affirmation) in " {} ".format(question.lower()):
                            self.say(choice(HAPPY))
                            return
                    for negation in NEGATION:
                        if " {} ".format(negation) in " {} ".format(question.lower()):
                            self.say(choice(SORRY))
                            return
                    self.say("I heard: {}, but I don't understand it!".format(utterance))
                return

            # Process Questions
            elif expression['utterance_type'] == 'question':
                result = self.app.brain.query_brain(expression)
                response = reply_to_question(result, list(self._objects))
                self.say(response.replace('_', ' '))

            # Process Statements
            elif expression['utterance_type'] == 'statement':
                result = self.app.brain.update(expression)
                response = reply_to_statement(result, self._speaker, list(self._objects), self)
                self.say(response.replace('_', ' '))

        else:  # No speaker is known
            self.say("I heard something, but I don't know who I'm talking to. Please show yourself to me!")

    def _tell_objects(self, new_objects):

        # If a single new object is seen, mention it with given certainty
        if len(new_objects) == 1:
            obj, confidence = new_objects[0]

            if confidence > 1 - config.OBJECT_CONFIDENCE_THRESHOLD / 4:
                self.say(choice(OBJECT_VERY_SURE).format(obj))
            elif confidence > 1 - config.OBJECT_CONFIDENCE_THRESHOLD / 2:
                self.say(choice(OBJECT_QUITE_SURE).format(obj))
            else:
                self.say(choice(OBJECT_NOT_SO_SURE).format(obj))

        # If multiple objects are seen, combine them in one happy expression
        elif len(new_objects) > 1:
            self.say("{} I see a {} and a {}!".format(
                choice(HAPPY), ", a ".join(obj for obj, conf in new_objects[:-1]), new_objects[-1][0]))


if __name__ == '__main__':
    # Boot Application
    app = SystemApp()  # Run on PC
    # app = NaoqiApp()  # Run on Robot

    # Boot Intention
    intention = ReactiveIntention(app)

    # Link Intention to App
    app.intention = intention

    # Start App (a.k.a. Start Microphone and Camera)
    app.start()
