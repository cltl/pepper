from pepper import ADDRESS, App, PepperCamera, CameraResolution
from scipy.misc import imsave
from queue import Queue
from threading import Thread

from time import time, sleep


class CameraTest(App):
    def __init__(self, address):
        """
        Test Pepper Cameras by displaying their feeds

        Parameters
        ----------
        address: (str, int)
            tuple of (<ip>, <port>)
        """
        super(CameraTest, self).__init__(address)
        self.camera = PepperCamera(self.session, resolution=CameraResolution.VGA_640x480, framerate=20)

        self.queue = Queue()

        for i in range(7):
            Thread(target=self.image_saver).start()

        index = 0
        mean = 0.0

        t0 = time()
        while True:
            image = self.camera.get()

            self.queue.put((index, image))

            elapsed_time = time() - t0
            mean = (index * mean + elapsed_time) / (index + 1)
            index += 1

            fps = 1/mean
            kbps = fps * image.nbytes / (1024**2)
            print "\r{} {:3.4f}fps : {:3.4f} MB/s".format(index, fps, kbps),
            t0 = time()
            sleep(1.0/float(self.camera.framerate))

    def image_saver(self):
        while True:
            index, image = self.queue.get()
            imsave("img/frame_{:04d}.png".format(index), image)



if __name__ == "__main__":
    app = CameraTest(ADDRESS)