from pepper.app import App
from pepper.vision.camera import PepperCamera, Resolution
from pepper.vision.classification.face import FaceRecognition
from pepper.vision.classification.data import load_faces, save_faces, load_lfw

import numpy as np

from threading import Thread
from time import time



class FaceApp(App):

    def __init__(self, address):
        super(FaceApp, self).__init__(address)

        self.speech = self.session.service("ALAnimatedSpeech")

        self.face_recognition = FaceRecognition()
        self.camera = PepperCamera(self.session, "PepperCamera12", Resolution.QQVGA)

        self.resources.append(self.camera)
        self.resources.append(self.face_recognition)

        self.names, self.vector = load_lfw()

        # lfw_names, lfw_vector = load_lfw()
        # face_names, face_vector = load_faces()
        # self.names = lfw_names + face_names
        # self.vector = np.concatenate((lfw_vector, face_vector))

        self.recent = []
        self.running = True
        Thread(target=self.check_faces).start()

    def check_faces(self):
        N_AVERAGES = 20
        THRESHOLD = 0.25

        recent_distance = 1

        while self.running:
            t = time()

            image = self.camera.get()
            face = self.face_recognition.represent(image)

            if face:
                bounds, representation = face

                self.recent.append(representation)

                name, distance = self.face_recognition.distance(representation, self.names, self.vector)[0]

                if distance < THRESHOLD:
                    print("Recognized {}".format((name, distance)))
                    self.speech.say("Hello, {}!".format(name))
                    self.recent = []

                elif len(self.recent) >= N_AVERAGES:
                    recent = np.array(self.recent[-N_AVERAGES:])
                    recent_mean = np.mean(recent, 0)
                    recent_distance = np.sum(np.mean(recent - recent_mean, 0) ** 2)

                    if recent_distance < THRESHOLD:
                        print("New Face! {}".format(recent_distance))
                        self.speech.say("I see a new face!")
                        self.names.append("Bram")
                        self.vector = np.concatenate((self.vector, recent_mean[None, :]))
                        self.recent = []

                    self.recent = self.recent[-N_AVERAGES:]

                print("[{}] ({:1.3f}s) {} ({})".format(
                    len(self.recent), time() - t, (name, distance), recent_distance))

    def stop(self):
        self.running = False
        super(FaceApp, self).stop()
        # save_faces(["Bram"], np.array(np.mean(self.representation, 0, keepdims=True)))


if __name__ == "__main__":
    FaceApp(("192.168.1.102", 9559)).run()