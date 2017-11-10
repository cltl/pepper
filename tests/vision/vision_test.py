from time import sleep

from pepper.app import App
from pepper.vision.camera import PepperCamera
from pepper.vision.classification.object import ObjectClassifyClient


class VisionTest(App):
    def __init__(self, address):
        super(VisionTest, self).__init__(address)

        self.camera = PepperCamera(self.session, "PepperCamera2")
        self.classify_client = ObjectClassifyClient(('localhost', 9999))

    def classify(self):
        while True:
            for confidence, object in self.classify_client.classify(self.camera.get()):
                print("[{:3.0%}] {}".format(confidence, object))
            sleep(5)


if __name__ == "__main__":
    VisionTest(["192.168.1.100", 9559]).classify()