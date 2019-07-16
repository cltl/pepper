from pepper.framework import *
from pepper import config


class ObjPosApp(AbstractApplication,
                DisplayComponent, SceneComponent,
                ExploreComponent, ContextComponent,
                ObjectDetectionComponent, SpeechRecognitionComponent, FaceRecognitionComponent, TextToSpeechComponent):

    def __init__(self, backend):
        super(ObjPosApp, self).__init__(backend)


if __name__ == '__main__':
    ObjPosApp(config.get_backend()).run()
