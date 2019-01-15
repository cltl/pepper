from pepper.framework import *
from pepper import config

from time import time


class GreetingApplication(AbstractApplication, FaceDetectionComponent, TextToSpeechComponent):

    GREET_TIMEOUT = 15  # Only Greet people once every X seconds

    def __init__(self, backend):
        """Greets New and Known People"""
        super(GreetingApplication, self).__init__(backend)

        self.nametime = {}  # Dictionary of <name, time> pairs, to keep track of who is greeted when

    def on_face_known(self, faces):
        """
        On Person Event.
        Called every time a known face is detected.
        """

        for person in faces:
            if self.is_greeting_appropriate(person.name):
                self.say("Hello, {}!".format(person.name))

    def on_face_new(self, faces):
        """
        On New Person Event.
        Called every time an unknown face is detected.
        """

        if self.is_greeting_appropriate("new"):
            self.say("I see {} new people!".format(len(faces)))

    def is_greeting_appropriate(self, name):
        """Returns True if greeting is appropriate and updates Greeting Time"""
        if name not in self.nametime or (time() - self.nametime[name]) > self.GREET_TIMEOUT:
            self.nametime[name] = time()
            return True
        return False


if __name__ == "__main__":
    # Run Application with Backend specified in Global Configuration File
    GreetingApplication(config.get_backend()).run()
