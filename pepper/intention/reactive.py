from pepper.framework.system import SystemApp
from pepper.framework import AbstractIntention
from pepper.language import classify_and_process_utterance, reply_to_question
from pepper.language.names import NameParser


class ReactiveIntention(AbstractIntention):
    def __init__(self, app):
        super(ReactiveIntention, self).__init__(app)

        self._parser = NameParser(list(self.app._faces.keys()))
        self._speaker = None

    def on_face_known(self, bounds, face, name):
        if name != self._speaker:
            self.log.info(name)
        self._speaker = name

    def on_transcript(self, transcript, audio):
        print(self._parser.parse(transcript, audio))

        # if self._speaker:
        #     expression = classify_and_process_utterance(transcript[0][0], self._speaker, 0, 0, [])  # TODO: Add Objects!!
        #
        #     print(expression)
        #
        #     if not expression or not 'utterance_type' in expression:
        #         return
        #
        #     if expression['utterance_type'] == 'question':
        #         result = self.app.brain.query_brain(expression)
        #         response = reply_to_question(result)
        #         self.text_to_speech.say(response)
        #         print(response)


if __name__ == '__main__':
    app = SystemApp()
    intention = ReactiveIntention(app)
    app.intention = intention
    app.start()
