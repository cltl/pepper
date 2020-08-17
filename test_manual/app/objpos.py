from pepper.app_container import ApplicationContainer
from pepper.framework.abstract.application import AbstractApplication
from pepper.framework.component import DisplayComponent, SceneComponent, ExploreComponent, ContextComponent, \
    ObjectDetectionComponent, SpeechRecognitionComponent, FaceRecognitionComponent, TextToSpeechComponent


class ObjPosApp(ApplicationContainer,
                AbstractApplication,
                DisplayComponent, SceneComponent,
                ExploreComponent, ContextComponent,
                ObjectDetectionComponent, SpeechRecognitionComponent, FaceRecognitionComponent, TextToSpeechComponent):

    def __init__(self, backend):
        super(ObjPosApp, self).__init__(backend)


if __name__ == '__main__':
    ObjPosApp().run()
