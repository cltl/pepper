from pepper.app import App
from pepper.input.camera import PepperCamera, CameraResolution, CameraColorSpace
from pepper.vision.classification.face import FaceRecognition
from pepper.output.led import Led

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


class Tracking(App):

    def __init__(self, address):
        super(Tracking, self).__init__(address)

        self.led = Led(self.session)

        self.camera = PepperCamera(self.session, resolution=CameraResolution.VGA_160x120, colorspace=CameraColorSpace.RGB)
        self.face = FaceRecognition()

        self.figure, self.axis = plt.subplots()
        self.preview = self.axis.imshow(self.camera.get().squeeze(), cmap='Greys_r')

        self.bounding_box = plt.Rectangle((0,0), 0, 0, fill=False, color='red')
        self.axis.add_patch(self.bounding_box)
        self.figure.colorbar(self.preview)

        self.animation = FuncAnimation(self.figure, self.get_frame, interval=1000/60.0)
        plt.show()

    def get_frame(self, i):
        image = self.camera.get()

        self.preview.set_data(image.squeeze())

        result = self.face.representation(image)

        if result:
            bounds, representation = result
            self.bounding_box.set_bounds(bounds.x, bounds.y, bounds.width, bounds.height)
            self.led.set((0, 1, 0))
        else:
            self.bounding_box.set_bounds(0,0,0,0)
            self.led.set((0, 0, 0))


if __name__ == "__main__":
    app = Tracking(('192.168.137.54', 9559))
