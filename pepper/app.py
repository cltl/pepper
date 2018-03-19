import pepper
from pepper.vision.face import FaceBounds


import qi
import logging
import time

from threading import Thread
from time import sleep



class App(object):
    def __init__(self, address):
        """
        Create Pepper Application.

        Parameters
        ----------
        address: (str, int)
            Peppers internet address: (ip, port)

        """
        self.resources = []

        self._address = address
        self._url = "tcp://{}:{}".format(*address)
        self._application = qi.Application([self.name, "--qi-url={}".format(self.url)])
        self._log = logging.getLogger(self.__class__.__name__)

        self.application.start()

    @property
    def log(self):
        """
        Get Logger for application

        Returns
        -------
        log: logging.Logger
        """
        return self._log

    @property
    def address(self):
        """
        Returns
        -------
        address : (str, int)
            Peppers internet address: (ip, port)
        """
        return self._address

    @property
    def url(self):
        """
        Returns
        -------
        url : str
            Peppers internet address: 'tcp://{ip}:{port}'
        """
        return self._url

    @property
    def name(self):
        """
        Returns
        -------
        name: str
            Name of Application, which is the name of the App (sub)class
        """
        return self.__class__.__name__

    @property
    def application(self):
        """
        Returns
        -------
        application: qi.Application
            Application object of the qi framework
        """
        return self._application

    @property
    def session(self):
        """
        Returns
        -------
        session: qi.Session
            Default Session of the qi Application
        """
        return self.application.session

    def start(self):
        """Start Application (Creating a Session)"""

        self.application.start()

    def run(self):
        """Run Application, Stopping on KeyboardInterrupt"""

        try:
            while True: time.sleep(1)
        except KeyboardInterrupt:
            print("KeyboardInterrupt, Closing Down!")
            self.stop()

    def stop(self):
        """Close Events and Stop Application"""
        for resource in self.resources:
            resource.close()
        self.application.stop()

    def __enter__(self):
        """Start Application when entering the 'with' statement."""
        self.start()

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop Application when exiting the 'with' statement"""
        self.stop()


class FlowApp(App):

    CAMERA_RESOLUTION = pepper.CameraResolution.VGA_320x240
    CAMERA_FREQUENCY = 2

    TEXT_TO_SPEECH_SPEED = 90

    def __init__(self, address):
        """
        Create Pepper Baseline Application

        Parameters
        ----------
        address: (str, int)
            Peppers internet address: (ip, port)
        """
        super(FlowApp, self).__init__(address)

        # Text to Speech
        self._tts = self.session.service("ALAnimatedSpeech")

        # Audio Stream
        self._microphone = pepper.PepperMicrophone(self.session)
        self._utterance = pepper.Utterance(self._microphone, self.on_utterance)

        # Camera Stream
        self._camera = pepper.PepperCamera(self.session, resolution=self.CAMERA_RESOLUTION)
        self._camera_thread = Thread(target=self._update_camera)

        # Face Detection
        self._openface = pepper.OpenFace()

        # Start processes
        self._utterance.start()
        self._camera_thread.start()
        self.log.info("Application Booted")

    def on_utterance(self, audio):
        """
        On Utterance Event

        Parameters
        ----------
        audio: numpy.ndarray
        """
        pass

    def on_face(self, bounds, representation):
        """
        On Face Detection

        Parameters
        ----------
        bounds: FaceBounds
        representation: np.ndarray
        """
        pass

    def on_camera(self, image):
        """
        On Camera Event

        Parameters
        ----------
        image: np.ndarray
        """

    def say(self, text):
        """
        Let Pepper Speak

        Parameters
        ----------
        text: str
        """
        self.log.info(u"Leolani: '{}'".format(text))
        self._utterance.stop()
        self._tts.say(r"\\rspd={}\\{}".format(self.TEXT_TO_SPEECH_SPEED, text))
        self._utterance.start()

    def _update_camera(self):
        while True:
            image = self._camera.get()
            self.on_camera(image)
            face = self._openface.represent(image)
            if face: self.on_face(*face)
            sleep(1.0 / self.CAMERA_FREQUENCY)  # Important to keep the rest working :)