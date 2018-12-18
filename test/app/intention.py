from pepper.framework import *
from pepper import config


class MyApplication(AbstractApplication, StatisticsComponent, FaceDetectionComponent, StreamedSpeechRecognitionComponent, TextToSpeechComponent):
    pass


class IdleIntention(AbstractIntention, MyApplication):
    def on_face_known(self, faces):
        TalkIntention(self.application)


class TalkIntention(AbstractIntention, MyApplication):
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
