from pepper.framework.abstract import AbstractComponent
from pepper.sensor.obj import CocoClassifyClient, CocoObject
from pepper import config

from threading import Thread
from Queue import Queue


class ObjectDetection(AbstractComponent):
    def __init__(self, backend):
        """
        Construct Object Detection Component

        Parameters
        ----------
        backend: AbstractBackend
        """
        super(ObjectDetection, self).__init__(backend)

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
            objects = [obj for obj in coco.classify(image) if obj.confidence > config.OBJECT_CONFIDENCE_THRESHOLD]
            queue.put((image, objects))

        def worker():
            """Object Detection Event Worker"""
            while True:
                image, objects = queue.get()

                # Call on_image Event Function
                self.on_image(image)

                # Call on_image Callback Functions
                for callback in self.on_image_callbacks:
                    callback(image)

                if objects:
                    # Call on_object Event Function
                    self.on_object(image, objects)

                    # Call on_object Callback Functions
                    for callback in self.on_object_callbacks:
                        callback(image, objects)

        # Initialize Object Queue & Worker
        thread = Thread(target=worker)
        thread.daemon = True
        thread.start()

        # Add on_image to Camera Callbacks
        self.backend.camera.callbacks += [on_image]

    def on_image(self, image):
        """
        On Image Event. Called every time an image was taken by Backend

        Parameters
        ----------
        image: np.ndarray
            Camera Frame
        """

    def on_object(self, image, objects):
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
