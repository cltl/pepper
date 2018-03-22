import pepper

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np

import os


class LearnFaceApp(pepper.App):

    FRAMES_PER_SECOND = 5
    RESOLUTION = pepper.CameraResolution.VGA_320x240

    def __init__(self, address, person_name):
        super(LearnFaceApp, self).__init__(address)

        self.camera = pepper.PepperCamera(self.session, resolution=self.RESOLUTION)
        self.openface = pepper.OpenFace()

        self.representation = []

        self.path = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'people', 'leolani', person_name + '.bin'))
        self.index = 0

        self.figure, self.axis = plt.subplots()
        self.preview = self.axis.imshow(self.camera.get())
        self.bounds = plt.Rectangle((0, 0), 0, 0, fill=False, color='green')
        self.axis.add_patch(self.bounds)

        self.animation = FuncAnimation(self.figure, self.update, interval=1000.0/self.FRAMES_PER_SECOND)
        plt.show()

    def update(self, i):
        image = self.camera.get()
        face = self.openface.represent(image)

        self.preview.set_data(image)

        if face:
            bounds, representation = face

            self.representation.append(representation)

            print "\r{}".format(self.index),
            self.index += 1

            self.bounds.set_bounds(bounds.x, bounds.y, bounds.width, bounds.height)
        else:
            self.bounds.set_bounds(0, 0, 0, 0)


if __name__ == "__main__":
    app = LearnFaceApp(pepper.ADDRESS, "NEW_PERSON")
    np.array(app.representation).tofile(app.path)

