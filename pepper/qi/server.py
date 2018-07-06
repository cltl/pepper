import qi
import socketserver
import json


class QiOutputHandler(socketserver.StreamRequestHandler):
    def handle(self):
        text = self.rfile.readline().strip()
        self.server.animated_speech.say(text)


class QiOutputServer(socketserver.TCPServer):
    def __init__(self, address, session):
        socketserver.TCPServer.__init__(self, address, QiOutputHandler)
        self.animated_speech = session.service("ALAnimatedSpeech")

class QiServer(object):
    def __init__(self):
        with open("../config.json") as config_json:
            config = json.load(config_json)

        self.url = "--qi-url=tcp://{}:{}".format(config['pepper-ip'], config['pepper-port'])
        self.application = qi.Application(["pepper-qi", self.url])
        self.application.start()

        print("Application Booted")

        self.output_address = (config['qi-ip'], config['qi-port-output'])

        QiOutputServer(self.output_address, self.application.session).serve_forever()


if __name__ == "__main__":
    server = QiServer()
