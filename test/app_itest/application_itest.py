import unittest
import mock

from time import sleep
import numpy as np

from pepper.framework.abstract.microphone import TOPIC as MIC_TOPIC
from pepper.framework.abstract.camera import TOPIC as CAM_TOPIC
from pepper.framework.sensor.api import FaceDetector, ObjectDetector, AbstractTranslator, AbstractASR, Object, \
    UtteranceHypothesis
from pepper.framework.util import Bounds

from pepper.framework.sensor.container import DefaultSensorContainer
from pepper.framework.component import ObjectDetectionComponent, FaceRecognitionComponent, SpeechRecognitionComponent

from pepper.framework.backend.container import BackendContainer
from pepper.framework.event.api import EventBusContainer
from pepper.framework.event.memory import SynchronousEventBusContainer
from pepper.framework.di_container import singleton
from pepper.framework.abstract import AbstractMicrophone, AbstractCamera, AbstractTextToSpeech, AbstractMotion, AbstractLed, AbstractTablet, AbstractImage
from pepper.framework.abstract.application import AbstractApplication
from pepper.framework.abstract.backend import AbstractBackend

from pepper import CameraResolution


TEST_IMG = np.zeros((128,))
TEST_BOUNDS = Bounds(0.0, 0.0, 1.0, 1.0)


class TestBackendContainer(BackendContainer, EventBusContainer):
    @property
    @singleton
    def backend(self):
        return TestBackend(self.event_bus)


class TestBackend(AbstractBackend):
    def __init__(self, event_bus):
        super(TestBackend, self).__init__(camera=AbstractCamera(CameraResolution.VGA, 1, event_bus),
                                          microphone=AbstractMicrophone(8000, 1, event_bus),
                                          text_to_speech=AbstractTextToSpeech("nl"),
                                          motion=AbstractMotion(),
                                          led=AbstractLed(),
                                          tablet=AbstractTablet())


class TestSensorContainer(DefaultSensorContainer):
    def asr(self, language):
        mock_asr = mock.create_autospec(AbstractASR)
        mock_asr.transcribe.side_effect = lambda audio: [UtteranceHypothesis("Test one two", 1.0)]

        return mock_asr

    def translator(self, source_language, target_language):
        mock_translator = mock.create_autospec(AbstractTranslator)
        mock_translator.translate.side_effect = lambda text: "Translated: " + text

        return mock_translator

    @property
    def face_detector(self):
        mock_face_detector = mock.create_autospec(FaceDetector)
        mock_face_detector.represent.side_effect = lambda image: [(TEST_IMG, TEST_BOUNDS)]

        return mock_face_detector

    def object_detector(self, target):
        mock_object_detector = mock.create_autospec(ObjectDetector)
        mock_object_detector.classify.side_effect = lambda image: [Object("test_object", 1.0, TEST_BOUNDS, image)]

        return mock_object_detector


class ApplicationContainer(TestBackendContainer, TestSensorContainer, SynchronousEventBusContainer):
    pass


class TestApplication(ApplicationContainer, AbstractApplication,
                      SpeechRecognitionComponent,
                      FaceRecognitionComponent,
                      ObjectDetectionComponent):
    def __init__(self):
        super(TestApplication, self).__init__()
        self.objects = []
        self.faces = []
        self.persons = []
        self.new_persons = []
        self.hypotheses = []

    def start(self):
        self.microphone.start()
        self.camera.start()

    def stop(self):
        self.microphone.stop()
        self.camera.stop()

    def on_object(self, objects):
        self.objects.extend(objects)

    def on_face(self, faces):
        self.faces.extend(faces)

    def on_person(self, persons):
        self.persons.extend(persons)

    def on_new_person(self, persons):
        self.new_persons.extend(persons)

    def on_transcript(self, hypotheses, audio):
        self.hypotheses.extend(hypotheses)


class ApplicationITest(unittest.TestCase):
    def setUp(self):
        self.application = TestApplication()

    def tearDown(self):
        self.application.stop()
        del self.application

    def test_mic_events(self):
        mic_events = []
        def handle_audio_event(event):
            mic_events.append(event)

        self.application.event_bus.subscribe(MIC_TOPIC, handle_audio_event)
        self.application.start()

        mic = self.application.microphone
        audio_frame = np.random.rand(80).astype(np.int16)
        mic.on_audio(audio_frame)

        self.await(lambda: len(mic_events) > 0, msg="mic event")

        self.assertEqual(len(mic_events), 1)
        np.testing.assert_array_equal(mic_events[0].payload, audio_frame)

        try:
            self.await(lambda: len(mic_events) > 1, max=5)
        except unittest.TestCase.failureException:
            # Expect no more audio events
            pass

    def test_camera_events(self):
        image_events = []

        def handle_image_event(event):
            image_events.append(event)

        self.application.event_bus.subscribe(CAM_TOPIC, handle_image_event)
        self.application.start()

        bounds = Bounds(0.0, 0.0, 1.0, 1.0)
        image = AbstractImage(np.zeros((2, 2, 3)), bounds)

        cam = self.application.camera
        cam.on_image(image)

        self.await(lambda: len(image_events) > 0, msg="images")

        self.assertEqual(len(image_events), 1)
        np.testing.assert_array_equal(image_events[0].payload, image)

        try:
            self.await(lambda: len(image_events) > 1, max=5)
        except unittest.TestCase.failureException:
            # Expect no more audio events
            pass

    def await(self, predicate, max=100, msg="predicate"):
        cnt = 0
        while not predicate() and cnt < max:
            sleep(0.01)
            cnt += 1

        if cnt == max:
            self.fail("Test timed out waiting for " + msg)