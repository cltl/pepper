from pepper import ADDRESS, App, PepperCamera, CameraResolution
from time import time

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


class CameraTest(App):

    FRAMERATE = 8

    def __init__(self, address):
        """
        Test Pepper Cameras by displaying their feeds

        Parameters
        ----------
        address: (str, int)
            tuple of (<ip>, <port>)
        """
        super(CameraTest, self).__init__(address)

        self.camera = PepperCamera(self.session, resolution=CameraResolution.VGA_320x240, framerate=self.FRAMERATE)

        self.figure, self.axis = plt.subplots()
        self.preview = self.axis.imshow(self.camera.get())

        self.average_time = 0

        self.animation = FuncAnimation(self.figure, self.get_frame, interval=1000.0/self.FRAMERATE)
        plt.show()

    def get_frame(self, i):
        t0 = time()
        image = self.camera.get()
        self.average_time = (i * self.average_time + (time() - t0)) / (i+1)

        print "\rAverage Time: {:3.3f}s ({:3.3f} fps)".format(self.average_time, 1/self.average_time),

        self.preview.set_data(image)


if __name__ == "__main__":
    app = CameraTest(ADDRESS)
