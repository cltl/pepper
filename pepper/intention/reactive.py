from pepper.framework.system import SystemApp
from pepper.framework import AbstractIntention
from pepper.language import *
from pepper.language.names import NameParser

from random import getrandbits


class ReactiveIntention(AbstractIntention):
    def __init__(self, app):
        super(ReactiveIntention, self).__init__(app)

        self._name_parser = NameParser(list(self.app._faces.keys()))
        self._speaker = None
        self._chat_id = None
        self._chat_turn = 0

    def on_face_known(self, bounds, face, name):
        if name != self._speaker:
            self.log.info(name)
            self._speaker = name
            self._chat_id = getrandbits(128)
            self._chat_turn = 0

    def on_transcript(self, transcript, audio):
        if self._speaker:
            utterance, confidence = self._name_parser.parse_known(transcript)
            expression = classify_and_process_utterance(
                utterance, self._speaker, self._chat_id, self._chat_turn, [])  # TODO: Add Objects!!
            self._chat_turn += 1

            if not expression or not 'utterance_type' in expression:
                return
            elif expression['utterance_type'] == 'question':
                result = self.app.brain.query_brain(expression)
                response = reply_to_question(result)
                self.text_to_speech.say(response)

            elif expression['utterance_type'] == 'statement':
                result = self.app.brain.update(expression)
                response = reply_to_statement(result, self._speaker)
                self.text_to_speech.say(response)



if __name__ == '__main__':
    app = SystemApp()
    intention = ReactiveIntention(app)
    app.intention = intention
    app.start()
