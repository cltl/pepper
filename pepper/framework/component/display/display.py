from pepper.framework import AbstractComponent, AbstractImage
from pepper.framework.component import *
from pepper.framework.util import Mailbox
from .server import DisplayServer

from threading import Thread, Lock

from PIL import Image
from io import BytesIO
import base64
import json

from time import time


class DisplayComponent(AbstractComponent):

    def __init__(self, backend):
        super(DisplayComponent, self).__init__(backend)

        server = DisplayServer()
        server_thread = Thread(target=server.start, name="DisplayServerThread")
        server_thread.daemon = True
        server_thread.start()

        face_recognition = self.require(DisplayComponent, FaceRecognitionComponent)  # type: FaceRecognitionComponent
        object_recognition = self.require(DisplayComponent, ObjectDetectionComponent)  # type: ObjectDetectionComponent
        context = self.require(DisplayComponent, ContextComponent)  # type: ContextComponent
        scene = self.require(DisplayComponent, SceneComponent) # type: SceneComponent

        self._display_info = {}

        update_mailbox = Mailbox()

        def update_worker():
            while True:
                image = update_mailbox.get()

                t0 = time()
                # Serialize Display Info
                serialized_info = json.dumps(self._display_info)
                serialized_info_time = time() - t0

                t0 = time()
                # Update Server with Display Info
                server.update(serialized_info)
                server_update_time = time() - t0

                t0 = time()
                # Get Scatter Coordinates
                x, y, z, c = scene.scatter_map
                scatter_map_time = time() - t0

                t0 = time()
                # Construct Display Info (to be send to webclient)
                self._display_info = {
                    "hash": hash(str(image.image)),
                    "img": encode_image(Image.fromarray(image.image)),
                    "frustum": image.frustum(0.25, 4),
                    "items": [],
                    "items3D": [{
                        "position": item.position,
                        "bounds3D": item.bounds3D
                    } for item in context.context.objects],

                    "x": x.tolist(),
                    "y": y.tolist(),
                    "z": z.tolist(),
                    "c": c.tolist()
                }

                display_info_time = time() - t0

                # total_time = display_info_time + scatter_map_time + server_update_time + serialized_info_time
                # print("{:3.3f} = {:3.3f} + {:3.3f} + {:3.3f} + {:3.3f}".format(
                #     total_time, serialized_info_time, server_update_time, scatter_map_time, display_info_time
                # ))

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

            update_mailbox.put(image)

        def add_items(items):
            if self._display_info:
                self._display_info["items"] += [
                    {"name": item.name,
                     "confidence": item.confidence,
                     "bounds": item.image_bounds.to_list(),
                     "position": item.position,
                     "bounds3D": item.bounds3D,
                     } for item in items]

        self.backend.camera.callbacks += [on_image]
        face_recognition.on_face_known_callbacks += [add_items]
        object_recognition.on_object_callbacks += [add_items]

        update_thread = Thread(target=update_worker, name="DisplayComponentUpdateThread")
        update_thread.daemon = True
        update_thread.start()
