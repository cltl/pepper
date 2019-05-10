from pepper.framework import *
from pepper import config


class ObjPosApp(AbstractApplication, StatisticsComponent, DisplayComponent, ContextComponent, SceneComponent,
                ObjectDetectionComponent, SpeechRecognitionComponent, FaceRecognitionComponent, TextToSpeechComponent):
    pass


if __name__ == '__main__':
    ObjPosApp(config.get_backend()).run()
