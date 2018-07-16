from pepper.framework.naoqi import *
from pepper.framework.object import InceptionClassifyClient


APP = NaoqiApp

class MyApp(APP):
    def __init__(self):
        super(MyApp, self).__init__()

        self._inception = InceptionClassifyClient()

    def on_face_known(self, bounds, face, name):
        self.log.info(name)

    def on_object(self, image, classes, scores, boxes):
        self.log.info(self._inception.classify(image))
        self.log.info(classes)

    def on_utterance(self, audio):
        # super(MyApp, self).on_utterance(audio)
        self.log.info("Utterance {:3.2f}s".format(len(audio) / float(self.microphone.rate)))

    def on_transcript(self, transcript):
        self.log.info(transcript)


if __name__ == '__main__':
    MyApp().run()