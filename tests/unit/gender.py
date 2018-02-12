from pepper import SystemCamera, OpenFace, GenderClassifyClient
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from scipy.misc import imresize
from time import time



class SystemCameraTest:

    SIZE = (240, 320)

    def __init__(self):

        self.openface = OpenFace()
        self.gender = GenderClassifyClient()

        self.camera = SystemCamera()
        self.figure, self.axis = plt.subplots()
        self.preview = self.axis.imshow(imresize(self.camera.get(), self.SIZE))
        self.bounds = plt.Rectangle((0,0), 0, 0, fill=False, color='green')
        self.axis.add_patch(self.bounds)
        self.animation = FuncAnimation(self.figure, self.process_frame, interval=1000 / 60.0)
        plt.show()

    def process_frame(self, i):
        image = imresize(self.camera.get(), self.SIZE)

        self.preview.set_data(image)
        face = self.openface.represent(image)

        if face:
            bounds, representation = face
            gender = self.gender.classify(representation)

            print(gender)
            self.bounds.set_color('pink' if gender > .5 else 'blue')
            self.bounds.set_bounds(bounds.x, bounds.y, bounds.width, bounds.height)
        else:
            self.bounds.set_bounds(0, 0, 0, 0)

if __name__ == "__main__":
    SystemCameraTest()
