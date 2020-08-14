"""Example Application that tells you what it sees"""

from time import time

from pepper.app_container import ApplicationContainer
from pepper.framework.abstract import AbstractApplication
from pepper.framework.component import ObjectDetectionComponent, TextToSpeechComponent


class ObjectApplication(ApplicationContainer,
                        AbstractApplication,        # Each Application inherits from AbstractApplication
                        ObjectDetectionComponent,   # Object Detection Component (using pepper_tensorflow)
                        TextToSpeechComponent):     # Text to Speech, for Speaking using the self.say method

    OBJECT_TIMEOUT = 15

    def __init__(self):
        # Initialize Superclasses (very, very important)
        super(ObjectApplication, self).__init__()

        # Keep track of which objects are seen when
        self.object_time = {}

    def on_object(self, objects):
        """
        On Object Event.
        Called every time one or more objects are detected in a camera frame.
        """

        # For each object in camera frame,
        for obj in objects:

            # Check whether speaking is appropriate
            if self.is_object_recognition_appropriate(obj.name):

                # Then tell human what you saw
                self.say("I see a {}".format(obj.name))

    def is_object_recognition_appropriate(self, name):
        """Returns True if telling about objects is appropriate and updates Object Time"""

        # Appropriateness arises when
        #  1. object hasn't been seen before, or
        #  2. enough time has passed since last sighting
        if name not in self.object_time or (time() - self.object_time[name] > self.OBJECT_TIMEOUT):

            # Store last seen time (right now) in object_time dictionary
            self.object_time[name] = time()

            # Return "Appropriate"
            return True

        # Return "Not Appropriate"
        return False


if __name__ == "__main__":
    ObjectApplication().run()
