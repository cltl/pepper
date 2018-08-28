from pepper.framework.system import SystemApp
from pepper.framework.naoqi import NaoqiApp

from pepper.framework import AbstractIntention
from pepper.language import *
from pepper.language.names import NameParser

from random import getrandbits


class ReactiveIntention(AbstractIntention):
    def __init__(self, app):
        super(ReactiveIntention, self).__init__(app)

        # The name parser is used to name-correct Google Speech outputs
        self._name_parser = NameParser(list(self.app._faces.keys()))

        # Speaker and Conversation info
        self._speaker = None
        self._chat_id = None
        self._chat_turn = 0

        # Set of Objects seen (passed to NLP as a list)
        self._objects = set()

    def on_face_known(self, bounds, face, name):

        # if recognised person is different from current person greet and initialize conversation
        if name != self._speaker:
            self.say("Hello, {}!".format(name))
            self._speaker = name
            self._chat_id = getrandbits(128)
            self._chat_turn = 0

    def on_object(self, image, objects):

        # Loop through currently visible objects, which are defined as (<name>, <confidence>, <bounding box>)
        for obj, confidence, bbox in objects:

            # if new object is not yet seen, mention it and add it to seen objects
            if obj not in self._objects:
                self.say("I see a {}".format(obj))
                self._objects.add(obj)

    def on_transcript(self, transcript, audio):
        if self._speaker:  # If Speaker is Recognized

            # Parse Names in Utterance
            utterance, confidence = self._name_parser.parse_known(transcript)

            # Parse Expression
            expression = classify_and_process_utterance(
                utterance, self._speaker, self._chat_id, self._chat_turn, list(self._objects))
            self._chat_turn += 1

            # Cancel if not a valid expression
            if not expression or not 'utterance_type' in expression:
                return

            # Process Questions
            elif expression['utterance_type'] == 'question':
                result = self.app.brain.query_brain(expression)
                response = reply_to_question(result)
                self.say(response)

            # Process Statements
            elif expression['utterance_type'] == 'statement':
                result = self.app.brain.update(expression)
                response = reply_to_statement(result, self._speaker)
                self.text_to_speech.say(response)



if __name__ == '__main__':
    # Boot Application
    # app = SystemApp()  # Run on PC
    app = NaoqiApp()  # Run on Robot

    # Boot Intention
    intention = ReactiveIntention(app)

    # Link Intention to App
    app.intention = intention

    # Start App (a.k.a. Start Microphone and Camera)
    app.start()
