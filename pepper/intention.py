from pepper.framework import AbstractIntention
from pepper.knowledge.wolfram import Wolfram


class IdleIntention(AbstractIntention):
    def on_face_new(self, bounds, face):
        self.app.intention = MeetIntention()

    def on_face_known(self, bounds, face, name):
        self.text_to_speech.say("Hello, {}".format(name))
        self.app.intention = QnAIntention()


class MeetIntention(AbstractIntention):
    pass


class QnAIntention(AbstractIntention):
    def __init__(self):
        super(QnAIntention, self).__init__()

        self.wolfram = Wolfram()

    def on_transcript(self, transcript):
        question = transcript[0][0]
        answer = self.wolfram.query(question)
        self.text_to_speech.say(answer)


if __name__ == '__main__':
    from pepper.framework.system import SystemApp
    SystemApp(IdleIntention()).start()