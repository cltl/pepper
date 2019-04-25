from pepper.framework import AbstractComponent, AbstractImage
from pepper.framework.component import FaceRecognitionComponent, ObjectDetectionComponent, SceneComponent
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

        face_recognition = self.require(DisplayComponent, FaceRecognitionComponent)  # type: FaceRecognitionComponent
        object_recognition = self.require(DisplayComponent, ObjectDetectionComponent)  # type: ObjectDetectionComponent
        scene = self.require(DisplayComponent, SceneComponent) # type: SceneComponent

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
            # type: (AbstractImage) -> None
            with lock:
                if self._display_info:
                    server.update(json.dumps(self._display_info))

                x,y,z,c = scene.scatter_map

                self._display_info = {
                    "hash": hash(str(image.image)),
                    "img": encode_image(Image.fromarray(image.image)),
                    "items": [],
                    "x": x.tolist(),
                    "y": y.tolist(),
                    "z": z.tolist(),
                    "c": c.tolist()
                }

        def add_items(items):
            if self._display_info:
                with lock:
                    self._display_info["items"] += [
                        {"name": item.name,
                         "confidence": item.confidence,
                         "bounds": item.image_bounds.to_list()
                         } for item in items]

        self.backend.camera.callbacks += [on_image]
        face_recognition.on_face_known_callbacks += [add_items]
        object_recognition.on_object_callbacks += [add_items]
