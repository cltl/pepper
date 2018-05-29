from pepper import ADDRESS, App, PepperCamera, CameraResolution
from time import time


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
        self.camera = PepperCamera(self.session, resolution=CameraResolution.VGA_320x240)

        index = 0
        mean = 0.0

        t0 = time()
        while True:
            image = self.camera.get()

            mean = (index * mean + (time() - t0)) / (index + 1)
            index += 1

            fps = 1/mean
            kbps = fps * image.nbytes / (1024**2)
            print "\r{:3.4f}fps : {:3.4f} MB/s".format(fps, kbps),
            t0 = time()


if __name__ == "__main__":
    app = CameraTest(ADDRESS)
