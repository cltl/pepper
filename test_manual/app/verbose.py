from pepper.app_container import ApplicationContainer
from pepper.framework.abstract.application import AbstractApplication
from pepper.framework.component import DisplayComponent, StatisticsComponent, CameraComponent, \
    SpeechRecognitionComponent, ObjectDetectionComponent, FaceRecognitionComponent


class VerboseApp(ApplicationContainer,
                 AbstractApplication, DisplayComponent, StatisticsComponent, CameraComponent,
                 SpeechRecognitionComponent, ObjectDetectionComponent, FaceRecognitionComponent):

    def on_image(self, image):
        self.log.info("on_image: {}".format(image))

    def on_object(self, objects):
        self.log.info("on_object: {}".format(objects))

    def on_face_known(self, faces):
        self.log.info("on_face: {}".format(faces))

    def on_face(self, faces):
        self.log.info("on_person: {}".format(faces))

    def on_face_new(self, faces):
        self.log.info("on_new_person: {}".format(faces))

    def on_transcript(self, hypotheses, audio):
        self.log.info("on_transcript: {}".format(hypotheses, audio.shape))


if __name__ == '__main__':
    VerboseApp().run()
