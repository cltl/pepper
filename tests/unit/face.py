import pepper
from threading import Thread
from time import time
from random import choice

import numpy as np


class FaceRecognitionApp(pepper.App):

    GREET_TIMEOUT = 15

    GREET = ["Hello", "Hi", "Hey There", "Greetings", "Good Day"]

    def __init__(self):
        super(FaceRecognitionApp, self).__init__(pepper.ADDRESS)

        self._text_to_speech = self.session.service("ALAnimatedSpeech")

        self._camera = pepper.PepperCamera(self.session)
        self._camera_thread = Thread(target=self._update_camera)

        self._open_face = pepper.OpenFace()
        self._people = pepper.PeopleClassifier.load_directory(pepper.PeopleClassifier.LEOLANI)
        self._people_classifier = pepper.PeopleClassifier(self._people)

        self._camera_thread.start()

        self._last_greeted_time = 0
        self._last_greeted_name = ""

        print("Booted")

    def on_camera(self, image):
        face = self._open_face.represent(image)
        if face: self.on_face(*face)

    def on_face(self, bounds, representation):
        name, confidence, distance = self._people_classifier.classify(representation)

        if confidence > 0.9:
            if name != self._last_greeted_name or time() - self._last_greeted_time > self.GREET_TIMEOUT:
                self._text_to_speech.say("{}, {}!".format(choice(self.GREET), name))
                self._last_greeted_name = name
                self._last_greeted_time = time()
        elif distance > 1:
            self._text_to_speech.say("How nice to meet you!")

            samples = []
            while len(samples) < 20:
                face = self._open_face.represent(self._camera.get())
                if face:
                    samples.append(face[1])
                    print(len(samples))

            self._people["Person"] = np.concatenate(samples).reshape(-1, 128)
            self._people_classifier = pepper.PeopleClassifier(self._people)




        print(name, confidence, distance)

    def _update_camera(self):
        while True:
            self.on_camera(self._camera.get())


if __name__ == "__main__":
    FaceRecognitionApp().run()