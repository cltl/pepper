import pepper

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np


class ObjectRecognitionApp(pepper.App):
    """
    Object Recognition App

    Visualises Objects Pepper Recognises with their respective Confidences.

    Please note that the object classify server found in pepper_tensorflow must be running!
    """

    OBJECT_CLASSIFY_SERVER_ADDRESS = ('localhost', 9999)

    FRAMES_PER_SECOND = 1
    RESOLUTION = pepper.CameraResolution.VGA_320x240
    FONT = {'fontsize': 25}

    def __init__(self, address):
        super(ObjectRecognitionApp, self).__init__(address)

        # Pepper Camera and Classification
        self.camera = pepper.PepperCamera(self.session, resolution=self.RESOLUTION)
        self.classification_client = pepper.ObjectClassifyClient(self.OBJECT_CLASSIFY_SERVER_ADDRESS)

        # Build Plot
        self.image = self.camera.get()
        self.classification = self.classification_client.classify(self.image)[::-1]

        self.figure, self.axes = plt.subplots(2, 1)
        self.preview = self.axes[0].imshow(self.camera.get())
        self.axes[0].set_xticks([])
        self.axes[0].set_yticks([])

        self.confidence = self.axes[1].barh(np.arange(len(self.classification)),
                                           [confidence for confidence, name in self.classification])
        self.axes[1].set_yticks(np.arange(len(self.classification)))
        self.axes[1].set_yticklabels([name[0] for confidence, name in self.classification], self.FONT)
        self.axes[1].set_xlim(0, 1)
        self.axes[1].set_xlabel("Confidence")
        self.axes[1].set_aspect(1.0/10)

        self.animation = FuncAnimation(self.figure, self.update, interval=1000.0/self.FRAMES_PER_SECOND)

        plt.get_current_fig_manager().window.showMaximized()
        plt.tight_layout(0)

        plt.show()

    def update(self, i):
        self.image = self.camera.get()
        self.classification = self.classification_client.classify(self.image)[::-1]

        self.preview.set_data(self.image)

        for rect, (confidence, name) in zip(self.confidence, self.classification):
            rect.set_width(confidence)
            rect.set_color((1 - confidence, confidence, 0, 1))

        self.axes[1].set_yticklabels([name[0] for confidence, name in self.classification], self.FONT)


if __name__ == "__main__":
    app = ObjectRecognitionApp(pepper.ADDRESS)
