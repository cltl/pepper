from pepper.framework.abstract import AbstractComponent
from pepper.framework.component import ObjectDetectionComponent, FaceDetectionComponent
from pepper.web.server import VideoFeedApplication
from pepper.util.image import ImageAnnotator
from pepper.framework.util import Mailbox

from PIL import Image

from Queue import Empty
from threading import Thread


class VideoDisplayComponent(AbstractComponent):
    def __init__(self, backend):
        """
        Construct VideoDisplay Component

        Parameters
        ----------
        backend: Backend
        """
        super(VideoDisplayComponent, self).__init__(backend)

        image_mailbox = Mailbox()
        object_mailbox = Mailbox()
        person_mailbox = Mailbox()

        self.backend.camera.callbacks.insert(0, lambda image: image_mailbox.put(image))

        object_detection = self.require_dependency(VideoDisplayComponent, ObjectDetectionComponent)  # type: ObjectDetectionComponent
        object_detection.on_object_callbacks.insert(0, lambda image, objects: object_mailbox.put((image, objects)))

        face_detection = self.require_dependency(VideoDisplayComponent, FaceDetectionComponent)  # type: FaceDetectionComponent
        face_detection.on_person_callbacks.insert(0, lambda persons: person_mailbox.put(persons))

        webapp = VideoFeedApplication()
        annotator = ImageAnnotator()

        def worker():
            while True:
                image = image_mailbox.get()

                persons = objects = []

                try: image, objects = object_mailbox.get(False)
                except Empty: pass

                try: persons = person_mailbox.get(False)
                except Empty: pass

                image = annotator.annotate(Image.fromarray(image), objects, persons)
                webapp.update(image)

        webapp_thread = Thread(target=webapp.start)
        webapp_thread.daemon = True
        webapp_thread.start()

        thread = Thread(target=worker)
        thread.daemon = True
        thread.start()


