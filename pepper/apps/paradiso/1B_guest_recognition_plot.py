import pepper
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


class GuestRecognitionPlot(pepper.App):

    def __init__(self, address):
        super(GuestRecognitionPlot, self).__init__(address)

        self.openface = pepper.OpenFace()

        self.camera = pepper.PepperCamera(self.session, resolution=pepper.CameraResolution.VGA_160x120)
        self.figure, self.axis = plt.subplots()
        self.preview = self.axis.imshow(self.camera.get())
        self.bounds = plt.Rectangle((0,0), 0, 0, fill=False, color='green', linewidth=10)

        self.representation = []

        self.axis.add_patch(self.bounds)
        self.animation = FuncAnimation(self.figure, self.process_frame, interval=1000 / 2.0)
        plt.xticks([])
        plt.yticks([])
        plt.tight_layout()
        plt.show()

    def process_frame(self, i):
        image = self.camera.get()

        self.preview.set_data(image)
        face = self.openface.represent(image)

        if face:
            bounds, representation = face
            self.bounds.set_bounds(bounds.x, bounds.y, bounds.width, bounds.height)
        else:
            self.bounds.set_bounds(0, 0, 0, 0)


if __name__ == "__main__":
    GuestRecognitionPlot(pepper.ADDRESS)
