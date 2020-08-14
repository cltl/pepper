from pepper.app_container import ApplicationContainer
from pepper.framework.abstract import AbstractApplication
from pepper.framework.component import StatisticsComponent, DisplayComponent, SceneComponent, ContextComponent, \
    ObjectDetectionComponent, FaceRecognitionComponent, SpeechRecognitionComponent, TextToSpeechComponent
from pepper.knowledge import animations

"""
HOWTO

1. (Re)Start Docker
2. Start Object Detection pepper_tensorflow/pepper_tensorflow/object_detection.py
3. Start This script!

"""


class BroaderMindApp(ApplicationContainer,
                     AbstractApplication,
                     StatisticsComponent,           # Show Performance Statistics in Terminal
                     DisplayComponent,              # Display what Robot (or Computer) sees in browser
                     SceneComponent,                # Scene (dependency of DisplayComponent)
                     ContextComponent,              # Context (dependency of DisplayComponent)
                     ObjectDetectionComponent,      # Object Detection (dependency of DisplayComponent)
                     FaceRecognitionComponent,      # Face Recognition (dependency of DisplayComponent)
                     SpeechRecognitionComponent,    # Speech Recognition Component (dependency)
                     TextToSpeechComponent):        # Text to Speech (dependency)

    def __init__(self):
        super(BroaderMindApp, self).__init__()

        self.context.start_chat("Human")

    def on_chat_turn(self, utterance):

        # TODO: Change animation to preferred animation
        self.say('hello! ... ...', animation=animations.AFFIRMATIVE)


if __name__ == '__main__':
    BroaderMindApp().run()
