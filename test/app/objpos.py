from pepper.framework import *
from pepper import config


class ObjPosApp(AbstractApplication, DisplayComponent, ContextComponent, SceneComponent,
                ObjectDetectionComponent, SpeechRecognitionComponent, FaceRecognitionComponent, TextToSpeechComponent):
    def on_object(self, objects):
        print(self.context.objects)


if __name__ == '__main__':
    ObjPosApp(config.get_backend()).run()
