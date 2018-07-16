import pepper
from pepper.vision.face import FaceBounds

import numpy as np
import qi

from threading import Thread
from time import sleep
import collections
import logging
import time



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


class SensorApp(App):

    PERSON_RECOGNITION_THRESHOLD = 0.9
    PERSON_NEW_THRESHOLD = 1.0

    CAMERA_RESOLUTION = pepper.CameraResolution.VGA_320x240
    CAMERA_FREQUENCY = 0.5

    def __init__(self, address, people = pepper.PeopleClassifier.load_directory(pepper.PeopleClassifier.LEOLANI)):

        super(SensorApp, self).__init__(address)

        # Text to Speech & Speech to Text
        self._text_to_speech = self.session.service("ALAnimatedSpeech")
        self._speech_to_text = pepper.GoogleASR()

        # Audio Stream
        self._microphone = pepper.PepperMicrophone(self.session)
        self._utterance = pepper.Utterance(self._microphone, self.on_utterance)
        self._name_recognition = pepper.NameRecognition()

        # Camera Stream
        self._camera = pepper.PepperCamera(self.session, resolution=self.CAMERA_RESOLUTION)
        self._camera_thread = Thread(target=self._update_camera)

        # Face Detection
        self._open_face = pepper.OpenFace()
        self._people = people
        self._people_classifier = pepper.PeopleClassifier(self._people)

        self._current_person = "person"

        self.speaking = False

        # Start processes
        self._utterance.start()
        self._camera_thread.start()
        self.log.info("Application Booted")

    @property
    def text_to_speech(self):
        return self._text_to_speech

    @property
    def microphone(self):
        return self._microphone

    @property
    def utterance(self):
        return self._utterance

    @property
    def open_face(self):
        return self._open_face

    @property
    def camera(self):
        return self._camera

    @property
    def current_person(self):
        return self._current_person

    def say(self, text, speed = 80):
        while self.speaking: sleep(0.1)

        self.speaking = True
        self.log.info(u"Leolani: '{}'".format(text))
        self._utterance.stop()
        self._text_to_speech.say(text)
        # self._text_to_speech.say(ur"\\rspd={}\\{}".format(speed, text))
        self._utterance.start()
        self.speaking = False

    def on_camera(self, image):
        face = self.open_face.represent(image)
        if face: self.on_face(*face)

    def on_face(self, bounds, representation):
        name, confidence, distance = self._people_classifier.classify(representation)
        if distance > self.PERSON_NEW_THRESHOLD:
            self.on_person_new()
        elif confidence > self.PERSON_RECOGNITION_THRESHOLD:
            self.on_person_recognized(name)

    def on_person_recognized(self, name):
        self.log.info("Recognized '{}'".format(name))

    def on_person_new(self):
        self.log.info("New Person!")

    def on_transcript(self, transcript, person):
        self.log.info("{}: '{}'".format(person, transcript))

    def on_utterance(self, audio):
        self.log.info("Utterance {:3.2f}s".format(float(len(audio)) / self.microphone.sample_rate))

        hypotheses = self._speech_to_text.transcribe(audio)

        if hypotheses:
            transcript, confidence = hypotheses[0]
            self.on_transcript(transcript, self.current_person)

    def _update_camera(self):
        while True:
            self.on_camera(self.camera.get())
            sleep(1.0 / self.CAMERA_FREQUENCY)  # Important to keep the rest working :)
