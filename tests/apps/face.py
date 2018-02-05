from pepper.app import App
from pepper.vision.camera import PepperCamera, CameraResolution
from pepper.vision.classification.face import FaceRecognition, PersonRecognition

import numpy as np
from threading import Thread


class FaceTest(App):

    MATRIX_PATH = r"C:\Users\Bram\Documents\Pepper\pepper\tests\data\lfw\submatrix.bin"
    NAMES_PATH = r"C:\Users\Bram\Documents\Pepper\pepper\tests\data\lfw\subnames.txt"

    def __init__(self, address):
        super(FaceTest, self).__init__(address)

        self.face = FaceRecognition()

        with open(FaceTest.NAMES_PATH) as name_file:
            self.person = PersonRecognition(names=name_file.read().split("\n"),
                                            matrix=np.fromfile(FaceTest.MATRIX_PATH, np.float32).reshape(-1, 128))

        self.index = 1
        self.pictures_of_new_person = 0
        self.new_person = []

        self.camera = PepperCamera(self.session, "FaceTest3", resolution=CameraResolution.QVGA)
        Thread(target = self._camera_thread).start()

        print("Face Test Program Booted")

    def on_camera(self, image):
        result = self.face.representation(image)

        if result:
            bounds, representation = result

            if self.pictures_of_new_person:

                print("Getting {} pictures of new person".format(self.pictures_of_new_person))

                self.new_person.append(representation)
                self.pictures_of_new_person -= 1

                if self.pictures_of_new_person == 0:
                    name = "Person {}".format(self.index)
                    self.person.add(name, np.mean(self.new_person, 0))
                    print("\nAdded {}\n".format(name))
                    self.index += 1

                    self.new_person = []

            else:
                classification = self.person.classify(representation)

                if classification:
                    if isinstance(classification, str):
                        print("\nrecognised {}\n".format(classification))
                    else:
                        self.pictures_of_new_person = 10


    def _camera_thread(self):
        while True:
            self.on_camera(self.camera.get())


if __name__ == "__main__":
    app = FaceTest(('192.168.137.54', 9559)).run()
