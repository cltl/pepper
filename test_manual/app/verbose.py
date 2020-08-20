from pepper.app_container import ApplicationContainer
from pepper.framework.abstract.microphone import TOPIC as MIC_TOPIC
from pepper.framework.abstract.camera import TOPIC as CAM_TOPIC
from pepper.framework.abstract.application import AbstractApplication
from pepper.framework.component import DisplayComponent, StatisticsComponent, \
    SpeechRecognitionComponent, ObjectDetectionComponent, FaceRecognitionComponent


class VerboseApp(ApplicationContainer,
                 AbstractApplication, DisplayComponent, StatisticsComponent,
                 SpeechRecognitionComponent, ObjectDetectionComponent, FaceRecognitionComponent):

    def __init__(self):
        self.event_bus.subscribe(MIC_TOPIC, lambda e: self._on_event("on_audio", e))
        self.event_bus.subscribe(CAM_TOPIC, lambda e: self._on_event("on_image", e))

    def _on_event(self, description, event):
        self.log.info((description + ": {}").format(event.payload))

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
