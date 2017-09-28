from pepper.image.camera import SystemCamera

from socket import socket
import yaml


class ClassifyClient:
    def __init__(self, address):
        self.address = address

    def classify(self, path):
        sock = socket()
        sock.connect(self.address)
        sock.sendall(path.encode())

        response = yaml.load(sock.recv(4096).decode())

        sock.close()

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
