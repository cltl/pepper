from pepper.framework.system import SystemApp


APP = SystemApp


class VerboseApp(APP):
    def __init__(self):
        super(VerboseApp, self).__init__()

    def on_utterance(self, audio):
        self.log.info("on_utterance: {:3.2f}s".format(len(audio) / float(self.microphone.rate)))

    def on_transcript(self, hypotheses, audio):
        for hypothesis in hypotheses:
            self.log.info("\ton_transcript: [{:4.0%}] {}".format(hypothesis.confidence, hypothesis.transcript))

    def on_face(self, faces):
        self.log.info("on_face: {}".format(faces))

    def on_face_known(self, persons):
        self.log.info("on_face_known: {}".format(persons))

    def on_object(self, image, objects):
        self.log.info("on_object: {} -> {}".format(image.shape, [obj.name for obj in objects]))


if __name__ == '__main__':
    VerboseApp().start()
