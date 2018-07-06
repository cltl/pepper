import subprocess
import threading
import socket
import json
import os


class QiClient:

    PYTHON27_32 = os.environ["PYTHON27_32"]
    QI_SERVER = os.path.join(os.path.dirname(__file__), "server.py")

    def __init__(self, address):
        self.server = subprocess.Popen([QiClient.PYTHON27_32, QiClient.QI_SERVER])
        threading.Thread(target=self.server.communicate).start()
        self.address = address

    def say(self, text: str):
        s = socket.socket()
        s.connect(self.address)
        s.sendall(text.encode())
        s.close()


if __name__ == "__main__":
    with open("../config.json") as config_json:
        config = json.load(config_json)

    client = QiClient((config['qi-ip'], config['qi-port-output']))

    while True:
        client.say(input("Text: "))
