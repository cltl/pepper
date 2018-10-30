from pepper.framework import *
from pepper import config


class MyApplication(Application, Statistics, FaceDetection, SpeechRecognition):
    pass


class IdleIntention(Intention, FaceDetection):
    def on_face(self, faces):
        TalkIntention(self.application)


class TalkIntention(Intention, SpeechRecognition):
    def __init__(self, application):
        super(TalkIntention, self).__init__(application)
        self.say("Hello, Human!")

    def on_transcript(self, hypotheses, audio):
        utterance = hypotheses[0].transcript

        if utterance == "bye bye":
            self.say("Goodbye, Human!")
            IdleIntention(self.application)
        else:
            self.say("How interesting!")


if __name__ == '__main__':

    # Initialize Application
    application = MyApplication(config.get_backend())

    # Run Intention
    IdleIntention(application)

    # Run Application
    application.run()
