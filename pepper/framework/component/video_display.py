from pepper.framework.abstract import AbstractComponent
from pepper.framework.component import ObjectDetection, FaceDetection
from pepper.web.server import VideoFeedApplication
from pepper.util.image import ImageAnnotator

from PIL import Image

from Queue import Queue, Empty
from threading import Thread


class VideoDisplay(AbstractComponent):
    def __init__(self, backend):
        """
        Construct VideoDisplay Component

        Parameters
        ----------
        backend: Backend
        """
        super(VideoDisplay, self).__init__(backend)

        image_queue = Queue()
        object_queue = Queue()
        person_queue = Queue()

        self.backend.camera.callbacks.append(lambda image: image_queue.put(image))

        object_detection = self.require_dependency(VideoDisplay, ObjectDetection)  # type: ObjectDetection
        object_detection.on_object_callbacks.append(lambda image, objects: object_queue.put((image, objects)))

        face_detection = self.require_dependency(VideoDisplay, FaceDetection)  # type: FaceDetection
        face_detection.on_person_callbacks.append(lambda persons: person_queue.put(persons))

        webapp = VideoFeedApplication()
        annotator = ImageAnnotator()

        def worker():
            while True:
                image = image_queue.get()

                objects = persons = []

                try: image, objects = object_queue.get(False)
                except Empty: pass

                try: persons = person_queue.get(False)
                except Empty: pass

                image = annotator.annotate(Image.fromarray(image), objects, persons)
                webapp.update(image)

        webapp_thread = Thread(target=webapp.start)
        webapp_thread.daemon = True
        webapp_thread.start()

        thread = Thread(target=worker)
        thread.daemon = True
        thread.start()


