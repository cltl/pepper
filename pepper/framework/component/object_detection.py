from pepper.framework.abstract import AbstractComponent
from pepper.framework.sensor.obj import ObjectDetectionClient, ObjectDetectionTarget, Object
from pepper.util import Scheduler, Mailbox
from pepper import config

import numpy as np

from typing import List, Dict


class ObjectDetectionComponent(AbstractComponent):

    TARGETS = config.OBJECT_RECOGNITION_TARGETS

    def __init__(self, backend):
        """
        Construct Object Detection Component

        Parameters
        ----------
        backend: AbstractBackend
        target: ObjectDetectionTarget
        """
        super(ObjectDetectionComponent, self).__init__(backend)

        # Callbacks
        self.on_object_callbacks = []

        clients = [ObjectDetectionClient(target) for target in ObjectDetectionComponent.TARGETS]
        mailboxes = {client: Mailbox() for client in clients}  # type: Dict[ObjectDetectionClient, Mailbox]

        def on_image(image, orientation):
            """
            Raw On Image Event. Called every time the camera yields a frame.

            Parameters
            ----------
            image: np.ndarray
            orientation: tuple
            """
            for client in clients:
                mailboxes[client].put(image)

        def worker(client):
            # type: (ObjectDetectionClient) -> None
            """Object Detection Event Worker"""
            image = mailboxes[client].get()

            objects = [obj for obj in client.classify(image) if obj.confidence > config.OBJECT_RECOGNITION_THRESHOLD]

            if objects:

                # Call on_object Callback Functions
                for callback in self.on_object_callbacks:
                    callback(image, objects)

                # Call on_object Event Function
                self.on_object(image, objects)

        # Initialize Object Queue & Worker
        schedule = [Scheduler(worker, args=(client,), name="{}Thread".format(client.target.name)) for client in clients]

        for s in schedule:
            s.start()

        # Add on_image to Camera Callbacks
        self.backend.camera.callbacks += [on_image]

    def on_object(self, image, objects):
        # type: (np.ndarray, List[Object]) -> None
        """
        On Object Event. Called every time one or more objects are detected in a camera frame.

        Parameters
        ----------
        image: np.ndarray
            Camera Frame
        objects: list of Object
            List of Object instances
        """
        pass

