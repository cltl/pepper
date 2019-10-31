from pepper.framework import *
from pepper.responder import *
#from pepper.responder.weather import WeatherResponder
from pepper.language import Utterance
from pepper import config


RESPONDERS = [
    GoodbyeResponder(), GreetingResponder(),  WeatherElserwhere(), WeatherResponder(), ThanksResponder()
]


class ResponderApp (AbstractApplication, StatisticsComponent, ContextComponent,
                    FaceRecognitionComponent, ObjectDetectionComponent,
                    SpeechRecognitionComponent, TextToSpeechComponent):

    def __init__(self, backend):
        super(ResponderApp, self).__init__(backend)

        self.response_picker = ResponsePicker(self, RESPONDERS)

        self.context.start_chat("Human")

    def on_chat_turn(self, utterance):
        # type: (Utterance) -> None

        self.response_picker.respond(utterance)


if __name__ == '__main__':
    ResponderApp(config.get_backend()).run()
