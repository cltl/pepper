from pepper.app import App
from pepper.vision.camera import PepperCamera, CameraID, CameraResolution, CameraColorSpace

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


class CameraTest(App):

    def __init__(self, address):
        super(CameraTest, self).__init__(address)

        self.cameras = [
            PepperCamera(self.session, CameraID.TOP),
            PepperCamera(self.session, CameraID.BOTTOM),
            PepperCamera(self.session, CameraID.DEPTH, CameraResolution.VGA_80x60, CameraColorSpace.DEPTH)
        ]

        self.figure, self.axes = plt.subplots(1, 3)
        self.previews = [self.axes[i].imshow(camera.get().squeeze(), cmap='magma_r') for i, camera in enumerate(self.cameras)]

        self.animation = FuncAnimation(self.figure, self.get_frame, interval=1000/60.0)
        plt.show()

    def get_frame(self, i):
        for preview, camera in zip(self.previews, self.cameras):
            preview.set_data(camera.get().squeeze())


if __name__ == "__main__":
    app = CameraTest(('192.168.137.54', 9559))
