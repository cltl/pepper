from pepper.framework import AbstractComponent
from pepper.framework.component import FaceDetectionComponent, ObjectDetectionComponent
from .server import DisplayServer

from threading import Thread, Lock

from PIL import Image
from io import BytesIO
import base64
import json


class DisplayComponent(AbstractComponent):
    def __init__(self, backend):
        super(DisplayComponent, self).__init__(backend)

        server = DisplayServer()
        server_thread = Thread(target=server.start)
        server_thread.daemon = True
        server_thread.start()

        lock = Lock()

        self._display_info = {}

        def encode_image(image):
            """
            Parameters
            ----------
            image: Image.Image
            Returns
            -------
            base64: str
                Base64 encoded PNG string
            """

            with BytesIO() as png:
                image.save(png, 'png')
                png.seek(0)
                return base64.b64encode(png.read())

        def on_image(image):
            with lock:
                if self._display_info:
                    server.update(json.dumps(self._display_info))

                self._display_info = {
                    "hash": hash(str(image)),
                    "img": encode_image(Image.fromarray(image)),
                    "items": []
                }

        def add_items(items):
            if self._display_info:
                with lock:
                    self._display_info["items"] += [
                        {"name": item.name,
                         "confidence": item.confidence,
                         "bounds": item.bounds.to_list()
                         } for item in items]

        face_recognition = self.require(DisplayComponent, FaceDetectionComponent)  # type: FaceDetectionComponent
        object_recognition = self.require(DisplayComponent, ObjectDetectionComponent)  # type: ObjectDetectionComponent

        self.backend.camera.callbacks += [on_image]
        face_recognition.on_person_callbacks += [lambda faces: add_items(faces)]
        object_recognition.on_object_callbacks += [lambda image, objects: add_items(objects)]
