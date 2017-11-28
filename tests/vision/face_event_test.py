from pepper.app import App
from pepper.vision.camera import PepperCamera, Resolution
from pepper.vision.classification.face import FaceRecognitionEvent
from pepper.vision.classification.data import load_lfw, load_faces
import numpy as np


class FaceEventApp(App):
    def __init__(self, address):
        super(FaceEventApp, self).__init__(address)

        self.people = 0

        self.camera = PepperCamera(self.session, "FaceEventAppCamera", Resolution.QVGA)
        self.resources.append(self.camera)

        self.recognition = FaceRecognitionEvent(self.session, self.on_face, self.on_new_face, self.camera, *load_lfw())
        self.resources.append(self.recognition)

        print("Application Started")
        while raw_input() != "stop": pass
        print("Shutting Down!")
        self.stop()
        exit()

    def on_face(self, distance, name):
        print("{:4.4f} {:20s}".format(distance, name))

    def on_new_face(self, representation):
        self.people += 1
        name = "Person[{}]".format(self.people)
        print("NEW FACE -> {}".format(name))
        self.recognition.add_face(name, representation)

if __name__ == "__main__":
    FaceEventApp(("192.168.1.102", 9559)).run()