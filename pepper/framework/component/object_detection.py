from threading import Lock

from typing import List, Dict

from pepper import config
from pepper.framework.abstract import AbstractImage
from pepper.framework.abstract.camera import TOPIC as CAM_TOPIC
from pepper.framework.abstract.component import AbstractComponent
from pepper.framework.util import Scheduler, Mailbox


class ObjectDetectionComponent(AbstractComponent):
    """
    Perform Object Detection using `Pepper Tensorflow <https://github.com/cltl/pepper_tensorflow>`_
    """

    # The Object Detection Servers to Target (See pepper_tensorflow)
    TARGETS = config.OBJECT_RECOGNITION_TARGETS

    def __init__(self):
        # type: () -> None
        super(ObjectDetectionComponent, self).__init__()

        self._log.info("Initializing ObjectDetectionComponent")

        # Public List of On Object Callbacks:
        # Allowing other Components to Subscribe to it
        self.on_object_callbacks = []

        # Create Object Detection Client and a Mailbox per Target
        # Make sure the corresponding server @ pepper_tensorflow is actually running
        clients = [self.object_detector(target) for target in ObjectDetectionComponent.TARGETS]
        mailboxes = {client: Mailbox() for client in clients}  # type: Dict[ObjectDetectionClient, Mailbox]

        lock = Lock()

        def on_image(event):
            # type: (Event) -> None
            """
            Raw On Image Event. Called every time the camera yields a frame.

            Parameters
            ----------
            event: Event
            """
            for client in clients:
                mailboxes[client].put(event.payload)

        def worker(client):
            # type: (ObjectDetector) -> None
            """Object Detection Worker"""

            # Get Image from Mailbox Corresponding with Client
            image = mailboxes[client].get()

            # Classify Objects in this Image using Client
            objects = [obj for obj in client.classify(image) if obj.confidence > config.OBJECT_RECOGNITION_THRESHOLD]

            if objects:

                with lock:

                    # Call on_object Callback Functions
                    for callback in self.on_object_callbacks:
                        callback(objects)

                    # Call on_object Event Function
                    self.on_object(objects)

        # Initialize & Start Object Workers
        schedule = [Scheduler(worker, args=(client,), name="{}Thread".format(type(client))) for client in clients]
        for s in schedule:
            s.start()

        self._log.info("Started Object Workers")

        # Subscribe to on_image events from Camera
        self.event_bus.subscribe(CAM_TOPIC, on_image)

    def on_object(self, objects):
        # type: (List[Object]) -> None
        """
        On Object Event. Called per ObjectDetectionTarget every time one or more objects are detected in a camera frame.

        Parameters
        ----------
        objects: list of Object
            List of Object instances
        """
        pass
