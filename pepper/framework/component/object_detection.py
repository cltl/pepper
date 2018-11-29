from pepper.framework.abstract import AbstractComponent
from pepper.sensor.obj import CocoClassifyClient, CocoObject
from pepper.framework.util import Scheduler
from pepper import config

import numpy as np

from Queue import Queue
from typing import List, NoReturn


class ObjectDetectionComponent(AbstractComponent):
    def __init__(self, backend):
        """
        Construct Object Detection Component

        Parameters
        ----------
        backend: AbstractBackend
        """
        super(ObjectDetectionComponent, self).__init__(backend)

        # Callbacks
        self.on_image_callbacks = []
        self.on_object_callbacks = []

        # Initialize Object Classifier
        coco = CocoClassifyClient()
        queue = Queue()

        def on_image(image):
            """
            Raw On Image Event. Called every time the camera yields a frame.

            Parameters
            ----------
            image: np.ndarray
            """
            objects = [obj for obj in coco.classify(image) if obj.confidence > config.OBJECT_RECOGNITION_THRESHOLD]
            queue.put((image, objects))

        def worker():
            """Object Detection Event Worker"""
            image, objects = queue.get()

            if objects:
                # Call on_object Event Function
                self.on_object(image, objects)

                # Call on_object Callback Functions
                for callback in self.on_object_callbacks:
                    callback(image, objects)

            # Call on_image Event Function
            self.on_image(image)

            # Call on_image Callback Functions
            for callback in self.on_image_callbacks:
                callback(image)

        # Initialize Object Queue & Worker
        schedule = Scheduler(worker, name="ObjectDetectionComponentThread")
        schedule.start()

        # Add on_image to Camera Callbacks
        self.backend.camera.callbacks += [on_image]

    def on_image(self, image):
        # type: (np.ndarray) -> NoReturn
        """
        On Image Event. Called every time an image was taken by Backend

        Parameters
        ----------
        image: np.ndarray
            Camera Frame
        """

    def on_object(self, image, objects):
        # type: (np.ndarray, List[CocoObject]) -> NoReturn
        """
        On Object Event. Called every time one or more objects are detected in a camera frame.

        Parameters
        ----------
        image: np.ndarray
            Camera Frame
        objects: list of CocoObject
            List of CocoObject instances
        """
        pass
