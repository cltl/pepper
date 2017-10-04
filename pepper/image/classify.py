from pepper.image.camera import SystemCamera

import socket
import yaml
import os

class ClassifyClient:
    def __init__(self, address):
        self.address = address

    def classify(self, path):
        s = socket.socket()
        s.connect(self.address)
        s.sendall(path.encode())
        response = yaml.load(s.recv(4096).decode())
        return response


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    TMP = os.getcwd() + r'\capture.jpg'

    client = ClassifyClient(('localhost', 9999))

    camera = SystemCamera()

    while True:
        image = camera.get()
        plt.imsave(TMP, image)

        predictions = client.classify(TMP)
        print "\r[{:3.2%}] {}".format(*predictions[0]),
