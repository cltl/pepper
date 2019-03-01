from pepper.framework import *
from pepper.responder import *
from pepper import config


class ResponderApp(AbstractApplication,
                   StatisticsComponent,
                   ContextComponent,
                   SpeechRecognitionComponent,
                   ObjectDetectionComponent,
                   FaceRecognitionComponent,
                   TextToSpeechComponent):

    def __init__(self, backend):
        super(ResponderApp, self).__init__(backend)

        self.response_picker = ResponsePicker(self, [
            GreetingResponder(),
            GoodbyeResponder(),
        ])

        self.start_chat("Human")
        self.say("What's up, {}!".format(self.chat.speaker))

    def on_chat_turn(self, utterance):
        self.response_picker.respond(utterance)


if __name__ == '__main__':
    ResponderApp(config.get_backend()).run()
