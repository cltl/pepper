import matplotlib.pyplot as plt
import numpy as np
import json

import socketserver
from threading import Thread


class Plot:

    NUM_CATEGORIES = 5
    FONT = {'fontsize': 25}

    def __init__(self):
        self.figure, self.axis = plt.subplots()
        self.bars = self.axis.barh(np.arange(self.NUM_CATEGORIES), np.ones(self.NUM_CATEGORIES))
        self.axis.set_yticks(np.arange(self.NUM_CATEGORIES))
        self.axis.set_yticklabels(["LABEL" for i in range(self.NUM_CATEGORIES)], self.FONT)
        self.axis.set_xlim(0, 1)
        plt.get_current_fig_manager().window.showMaximized()
        plt.tight_layout()

    def update(self, classification):
        for bar, (confidence, labels) in zip(self.bars, classification[::-1]):
            bar.set_width(confidence)
            bar.set_color((1 - confidence, confidence, 0, 1))

        self.axis.set_yticklabels([name[0] for confidence, name in classification[::-1]], self.FONT)
        self.figure.canvas.draw()

class PlotHandler(socketserver.BaseRequestHandler):
    def handle(self):
        print("Update Plot")
        self.server.plot.update(json.loads(self.request.recv(4096)))

class PlotServer(socketserver.TCPServer):
    def __init__(self, address):
        self.plot = Plot()
        socketserver.TCPServer.__init__(self, address, PlotHandler, True)
        Thread(target=self.serve_forever).start()

if __name__ == "__main__":
    PlotServer(('', 47282))
    print("Plot Server Running")
    plt.show()