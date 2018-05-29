from pepper import ADDRESS, App, PepperCamera, CameraTarget, CameraResolution, CameraColorSpace

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

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

        self.cameras = [
            PepperCamera(self.session, CameraTarget.TOP),
            PepperCamera(self.session, CameraTarget.BOTTOM),
            PepperCamera(self.session, CameraTarget.DEPTH, CameraResolution.VGA_80x60, CameraColorSpace.DEPTH)
        ]

        self.figure, self.axes = plt.subplots(1, 3)
        self.previews = [self.axes[i].imshow(camera.get().squeeze(), cmap='Greys') for i, camera in enumerate(self.cameras)]

        self.animation = FuncAnimation(self.figure, self.get_frame, interval=1000/60.0)
        plt.show()

    def get_frame(self, i):
        for preview, camera in zip(self.previews, self.cameras):
            preview.set_data(camera.get().squeeze())


if __name__ == "__main__":
    app = CameraTest(ADDRESS)
