from pepper.framework import *
from pepper import config


class VerboseApp(AbstractApplication, StatisticsComponent, SpeechRecognitionComponent, ObjectDetectionComponent, FaceRecognitionComponent):
    def on_image(self, image, orientation):
        self.log.info("on_image: {} {}".format(image.shape, orientation))

    def on_object(self, image, objects):
        self.log.info("on_object: {} {}".format(image.shape, objects))

    def on_face_known(self, faces):
        self.log.info("on_face: {}".format(faces))

    def on_face(self, faces):
        self.log.info("on_person: {}".format(faces))

    def on_face_new(self, faces):
        self.log.info("on_new_person: {}".format(faces))

    def on_transcript(self, hypotheses, audio):
        self.log.info("on_transcript: {}".format(hypotheses, audio.shape))


if __name__ == '__main__':
    VerboseApp(config.get_backend()).run()
