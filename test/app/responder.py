from pepper.framework import *
from pepper.responder import *
from pepper import config


class ResponderApp(AbstractApplication,
                   StatisticsComponent,
                   ContextComponent,
                   BrainComponent,
                   SpeechRecognitionComponent,
                   ObjectDetectionComponent,
                   FaceRecognitionComponent,
                   TextToSpeechComponent):

    def __init__(self, backend):
        super(ResponderApp, self).__init__(backend)

        self.response_picker = ResponsePicker(self, [
            GreetingResponder(),
            GoodbyeResponder(),
            ThanksResponder(),
            AffirmationResponder(),
            NegationResponder(),
            QnAResponder(),
            VisionResponder(),
            PreviousUtteranceResponder(),
            IdentityResponder(),
            LocationResponder(),
            WikipediaResponder(),
            BrainResponder(),
        ])

    def on_person_enter(self, person):
        self.context.start_chat(person.name)
        self.say("Hello, {}".format(person.name))

    def on_person_exit(self):
        self.say("You are gone!")
        self.context.stop_chat()

    def on_chat_turn(self, utterance):
        self.response_picker.respond(utterance)


if __name__ == '__main__':
    ResponderApp(config.get_backend()).run()
