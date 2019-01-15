from pepper.framework import *
from pepper import config


class DisplayApp(AbstractApplication,
                 StatisticsComponent,
                 DisplayComponent,
                 ObjectDetectionComponent,
                 FaceDetectionComponent,
                 StreamedSpeechRecognitionComponent):

    pass


if __name__ == '__main__':
    DisplayApp(config.get_backend()).run()
