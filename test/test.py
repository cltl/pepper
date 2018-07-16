from pepper.framework.system import *


APP = SystemApp

class MyApp(APP):
    def __init__(self):
        super(MyApp, self).__init__()

    def on_face_known(self, bounds, face, name):
        self.log.info(name)

    def on_object(self, classes, scores, boxes):
        self.log.info(classes)

    def on_transcript(self, transcript):
        self.log.info(transcript)


if __name__ == '__main__':
    MyApp().run()