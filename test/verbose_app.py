from pepper.framework.system import SystemApp
from pepper.framework import AbstractIntention

APP = SystemApp


class VerboseApp(APP):
    def __init__(self):
        super(VerboseApp, self).__init__()

    def on_utterance(self, audio):
        self.log.info("on_utterance: {:3.2f}s".format(len(audio) / float(self.microphone.rate)))

    def on_transcript(self, hypotheses, audio):
        self.log.info("on_transcript: {}".format(hypotheses))

    def on_face(self, bounds, face):
        self.log.info("on_face: {} {}".format(bounds, face.shape))

    def on_face_known(self, bounds, face, name):
        self.log.info("on_face_known: {} {} {}".format(bounds, face.shape, name))

    def on_face_new(self, bounds, face):
        self.log.info("on_face_new: {} {}".format(bounds, face.shape))

    def on_object(self, image, objects):
        self.log.info("on_object: {} -> {}".format(image.shape, [cls for (cls, scr, box) in objects]))

if __name__ == '__main__':
    VerboseApp().start()
