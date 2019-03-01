from pepper.framework import *
from pepper import config


class TrackApp(AbstractApplication, StatisticsComponent, TrackComponent, DisplayComponent, ObjectDetectionComponent, FaceRecognitionComponent, SpeechRecognitionComponent):
    def __init__(self, backend):
        super(TrackApp, self).__init__(backend)


if __name__ == '__main__':
    TrackApp(config.get_backend()).run()
