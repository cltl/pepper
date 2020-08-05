from pepper.framework import *
from pepper.responder import *

from pepper import config

RESPONDERS = [
    WikipediaResponder(), WolframResponder()
]


class FactCheckingApp(AbstractApplication, StatisticsComponent,
                      ObjectDetectionComponent, FaceRecognitionComponent,
                      SpeechRecognitionComponent, TextToSpeechComponent):

    def __init__(self, backend):
        super(FactCheckingApp, self).__init__(backend)


class DefaultIntention(AbstractIntention, FactCheckingApp):
    IGNORE_TIMEOUT = 60

    def __init__(self, application):
        super(DefaultIntention, self).__init__(application)
        self.response_picker = ResponsePicker(self, RESPONDERS)

    def on_chat_turn(self, utterance):
        responder = self.response_picker.respond(utterance)


if __name__ == '__main__':
    # Initialize Application
    application = FactCheckingApp(config.get_backend())

    # Initialize Intention
    DefaultIntention(application)

    # Run Application
    application.run()
