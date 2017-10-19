import subprocess
from threading import Thread
from enum import Enum
from time import sleep

class KaldiModel(Enum):
    TEDLIUM = r"tedlium_nnet_ms_sp_online.yaml"


class KaldiServer(Thread):

    SERVER_IMAGE = r"jcsilva/docker-kaldi-gstreamer-server:latest"
    MODEL_DIRECTORY = r"c:/Users/Bram/Documents/Pepper/pepper/pepper/speech/kaldi/models"
    WORKING_DIRECTORY = r"/opt/models"

    def __init__(self, port, model = KaldiModel.TEDLIUM, daemon = False):
        """
        Run Docker Kaldi Server

        # Please ensure you have installed:
        # 1. Docker (https://www.docker.com/)
        # 2. docker-kaldi-gstreamer-server:latest (docker pull jcsilva/docker-kaldi-gstreamer-server:latest)

        Parameters
        ----------
        port: int
            Server port
        model: KaldiModel
            Model Kaldi should use
        daemon: bool
            Whether server should run as daemon or not
        """
        super(KaldiServer, self).__init__(target=self.run)
        self._port = port
        self._model = model

        self.daemon = daemon
        self.start()

        sleep(1)

        subprocess.call(['docker', 'exec', '-d',
                         self.__class__.__name__,
                         '/opt/start.sh',
                         '-y', "{}/{}".format(self.WORKING_DIRECTORY, self.model.value)])

        print("Kaldi Server Booted")

    @property
    def port(self):
        return self._port

    @property
    def model(self):
        return self._model

    def run(self):
        # Run Docker image in container
        subprocess.call(['docker', 'run',
                         # keeping connection open
                         '-i',
                         # automatically removing on exit
                         '--rm',
                         # Name of container
                         '--name', self.__class__.__name__,
                         # Port of container
                         '-p', "{}:80".format(self.port),
                         # Bind mount the model directory volume
                         '-v', "{}:{}".format(self.MODEL_DIRECTORY, self.WORKING_DIRECTORY),
                         # Set working directory
                         '-w', self.WORKING_DIRECTORY,
                         # Call Kaldi gstreamer sever image
                         self.SERVER_IMAGE])




if __name__ == "__main__":
    kaldi_server = KaldiServer(8080)