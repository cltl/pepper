from pepper.framework import *
from pepper.knowledge import animations
from pepper import config

"""
HOWTO

1. (Re)Start Docker
2. Start Object Detection pepper_tensorflow/pepper_tensorflow/object_detection.py
3. Start This script!

"""


class BroaderMindApp(AbstractApplication,
                     StatisticsComponent,           # Show Performance Statistics in Terminal
                     DisplayComponent,              # Display what Robot (or Computer) sees in browser
                     SceneComponent,                # Scene (dependency of DisplayComponent)
                     ContextComponent,              # Context (dependency of DisplayComponent)
                     ObjectDetectionComponent,      # Object Detection (dependency of DisplayComponent)
                     FaceRecognitionComponent,      # Face Recognition (dependency of DisplayComponent)
                     SpeechRecognitionComponent,    # Speech Recognition Component (dependency)
                     TextToSpeechComponent):        # Text to Speech (dependency)

    def __init__(self, backend):
        super(BroaderMindApp, self).__init__(backend)

        self.context.start_chat("Human")

    def on_chat_turn(self, utterance):

        # TODO: Change animation to preferred animation
        self.say('hello! ... ...', animation=animations.AFFIRMATIVE)


if __name__ == '__main__':
    BroaderMindApp(config.get_backend()).run()
