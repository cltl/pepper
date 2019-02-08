from pepper.framework import *
from pepper import config


class DisplayApp(AbstractApplication,
                 StatisticsComponent,
                 DisplayComponent,
                 ObjectDetectionComponent,
                 FaceDetectionComponent,
                 SpeechRecognitionComponent):

    pass


if __name__ == '__main__':
    DisplayApp(config.get_backend()).run()
