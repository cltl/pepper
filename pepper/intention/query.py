from pepper.framework.system import SystemApp

from pepper.framework import AbstractIntention

from pepper.knowledge.wolfram import Wolfram
from pepper.knowledge.query import QnA

from pepper.knowledge.sentences import *
from random import choice


class QueryIntention(AbstractIntention):
    def __init__(self, app):
        super(QueryIntention, self).__init__(app)

        self._qna = QnA()
        self._wolfram = Wolfram()
        self._name = None

    def on_face_new(self, bounds, face):
        if not self._name:
            self._name = None
            self.say("O hey, human!")

    def on_face_known(self, bounds, face, name):
        if self._name != name:
            self._name = name
            self.say("{} {} {}".format(choice(GREETING), name, choice(TELL_KNOWN)))

    def on_transcript(self, hypotheses, audio):
        question = hypotheses[0].transcript

        answer = self._qna.query(question)

        if not answer:
            answer = self._wolfram.query(question)

        if answer:
            if self._name:
                self.say("{} {}, {}".format(choice(["Well", "Look", "You see"]), self._name, answer))
            else:
                self.say(answer)
        else:
            self.say(choice(NO_ANSWER))


if __name__ == '__main__':
    # Boot Application
    app = SystemApp()  # Run on PC

    # Boot Intention
    intention = QueryIntention(app)

    # Link Intention to App
    app.intention = intention

    # Start App (a.k.a. Start Microphone and Camera)
    app.start()
