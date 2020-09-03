import logging
import sys
import threading
import unittest
from time import sleep

import mock
import numpy as np

from pepper.framework.abstract import AbstractMicrophone, AbstractTextToSpeech
from pepper.framework.abstract.application import AbstractApplication
from pepper.framework.abstract.backend import AbstractBackend
from pepper.framework.backend.container import BackendContainer
from pepper.framework.component import SpeechRecognitionComponent, TextToSpeechComponent
from pepper.framework.di_container import singleton
from pepper.framework.event.api import EventBusContainer
from pepper.framework.event.memory import SynchronousEventBusContainer
from pepper.framework.resource.api import ResourceContainer
from pepper.framework.resource.threaded import ThreadedResourceContainer
from pepper.framework.sensor.api import AbstractTranslator, AbstractASR, UtteranceHypothesis, SensorContainer
from pepper.framework.sensor.vad import WebRtcVAD


logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(stream=sys.stdout))
logger.setLevel(logging.ERROR)


AUDIO_FRAME = np.zeros(80).astype(np.int16)


def setupTestComponents():
    """Workaround to overwrite static state in DIContainers across tests"""
    global TestApplication

    class TestBackendContainer(BackendContainer, EventBusContainer, ResourceContainer):
        @property
        @singleton
        def backend(self):
            return TestBackend(self.event_bus, self.resource_manager)


    class TestTextToSpeech(AbstractTextToSpeech):
        def __init__(self, resource_manager):
            super(TestTextToSpeech, self).__init__("nl", resource_manager)
            self.latch = threading.Event()
            self.utterances = []

        def on_text_to_speech(self, text, animation=None):
            # type: (Union[str, unicode], Optional[str]) -> None
            self.latch.wait()
            self.utterances.append(text)


    class TestBackend(AbstractBackend):
        def __init__(self, event_bus, resource_manager):
            super(TestBackend, self).__init__(camera=None, microphone=AbstractMicrophone(8000, 1, event_bus, resource_manager),
                                              text_to_speech=TestTextToSpeech(resource_manager),
                                              motion=None, led=None, tablet=None)
            # TODO
            # resource_manager.provide_resource(MIC_TOPIC)


    class TestVAD(WebRtcVAD):
        def __init__(self, microphone, event_bus, resource_manager):
            super(TestVAD, self).__init__(microphone, event_bus, resource_manager)
            self.speech_flag = ThreadsafeBoolean()

        def _is_speech(self, frame):
            return self.speech_flag.val


    class TestSensorContainer(BackendContainer, SensorContainer, EventBusContainer):
        @property
        @singleton
        def vad(self):
            return TestVAD(self.microphone, self.event_bus, self.resource_manager)

        def asr(self, language="nl"):
            mock_asr = mock.create_autospec(AbstractASR)
            mock_asr.transcribe.side_effect = lambda audio: [UtteranceHypothesis("Test one two", 1.0)]

            return mock_asr

        def translator(self, source_language, target_language):
            mock_translator = mock.create_autospec(AbstractTranslator)
            mock_translator.translate.side_effect = lambda text: "Translated: " + text

            return mock_translator

        @property
        def face_detector(self):
            return None

        def object_detector(self, target):
            return None


    class ApplicationContainer(TestBackendContainer,
                               TestSensorContainer,
                               SynchronousEventBusContainer,
                               ThreadedResourceContainer):
        pass


    class TestApplication(ApplicationContainer, AbstractApplication,
                          SpeechRecognitionComponent, TextToSpeechComponent):
        def __init__(self):
            super(TestApplication, self).__init__()
            self.hypotheses = []

        def start(self):
            self.microphone.start()

        def stop(self):
            self.microphone.stop()

        def on_transcript(self, hypotheses, audio):
            self.hypotheses.extend(hypotheses)


class ListeningThread(threading.Thread):
    def __init__(self, speech_flag, microphone, name="Listening"):
        super(ListeningThread, self).__init__(name=name)
        self._speech_flag = speech_flag
        self._microphone = microphone
        self.running = True
        self.listen_to_frames = False
        self.listening_latch = threading.Event()
        self.exit_latch = threading.Event()
        self.continue_speech_latch = threading.Event()
        self.in_speech_latch = threading.Event()

    def stop(self):
        self.running = False
        self.listening_latch.set()
        self.exit_latch.set()
        self.continue_speech_latch.set()
        self.in_speech_latch.set()

    def listen(self, frames, continue_latch=False):
        self.in_speech_latch = threading.Event()
        self.continue_speech_latch = threading.Event()
        self.exit_latch = threading.Event()
        self.listen_to_frames = frames
        self.listening_latch.set()

        if continue_latch:
            return self.in_speech_latch, self.exit_latch, self.continue_speech_latch
        else:
            self.continue_speech_latch.set()
            return self.in_speech_latch, self.exit_latch

    def run(self):
        logger.debug("Thread %s started", self.name)
        self.listening_latch.wait()
        while self.running:
            logger.debug("Started listening")
            for i in range(self.listen_to_frames):
                self._speech_flag.val = True
                # Fill speech buffer
                for j in range(2*WebRtcVAD.BUFFER_SIZE + 10):
                    self._microphone.on_audio(AUDIO_FRAME)
                    logger.debug("Listened %s-%s", i, j)
                    sleep(0.001)

                self.in_speech_latch.set()
                self.continue_speech_latch.wait()

                self._speech_flag.val = False
                # Empty speech buffer
                for j in range(WebRtcVAD.BUFFER_SIZE + 10):
                    self._microphone.on_audio(AUDIO_FRAME)
                    logger.debug("Void %s-%s", i, j)
                    sleep(0.001)

            self.listening_latch.clear()
            logger.debug("Stopped listening")
            self.exit_latch.set()
            self.listening_latch.wait()

        logger.debug("Thread %s stopped", self.name)

class TalkingThread(threading.Thread):
    def __init__(self, text_to_speech, name="Talking"):
        super(TalkingThread, self).__init__(name=name)
        self._text_to_speech = text_to_speech
        self.running = True
        self.talking = False
        self.talking_latch = threading.Event()
        self.exit_latch = threading.Event()

    def stop(self):
        self.running = False
        self.talking_latch.set()
        self.exit_latch.set()

    def talk(self, utterances):
        self.exit_latch = threading.Event()
        self.utterances = utterances
        self.talking_latch.set()

        return self.exit_latch

    def run(self):
        logger.debug("Thread % started", self.name)
        self.talking_latch.wait()
        while self.running:
            logger.debug("Started talking")
            for utterance in self.utterances:
                self._text_to_speech.say(utterance, block=True)
                logger.debug("Said utterance")
                sleep(0.001)

            self.talking_latch.clear()
            logger.debug("Stopped talking")
            self.exit_latch.set()
            self.talking_latch.wait()

        logger.debug("Thread %s stopped", self.name)


class ResourceITest(unittest.TestCase):
    def setUp(self):
        setupTestComponents()
        self.application = TestApplication()
        self.application.start()
        self.threads = [ListeningThread(self.application.vad.speech_flag, self.application.microphone),
                        TalkingThread(self.application.text_to_speech)]
        for thread in self.threads:
            thread.start()

    def tearDown(self):
        for thread in self.threads:
            thread.stop()
            thread.join()
        self.application.stop()
        del self.application

    def test_listen(self):
        listening_thread, _ = self.threads

        _, exit_speech_latch = listening_thread.listen(2)
        exit_speech_latch.wait()

        sleep(0.1)

        self.assertEqual(2, len(self.application.hypotheses))
        self.assertEqual('Test one two', self.application.hypotheses[0].transcript)
        self.assertEqual(1.0, self.application.hypotheses[0].confidence)
        self.assertEqual('Test one two', self.application.hypotheses[1].transcript)
        self.assertEqual(1.0, self.application.hypotheses[1].confidence)

    def test_talk(self):
        self.application.text_to_speech.latch.set()

        _, talking_thread = self.threads

        talk_latch = talking_thread.talk(["Test"])

        self.assertTrue(talk_latch.wait())

        sleep(0.1)

        self.assertEqual(1, len(self.application.text_to_speech.utterances))
        self.assertEqual("Test", self.application.text_to_speech.utterances[0])

    def test_talk_after_vad_stops(self):
        self.application.text_to_speech.latch.set()
        listening_thread, talking_thread = self.threads

        in_speech_latch, exit_speech_latch, continue_speech_latch = listening_thread.listen(1, continue_latch=True)
        in_speech_latch.wait()

        exit_talk_latch = talking_thread.talk(["Test"])
        self.assertFalse(exit_talk_latch.wait(0.5))

        continue_speech_latch.set()
        exit_speech_latch.wait()

        exit_talk_latch.wait()

        sleep(0.1)

        self.assertEqual(1, len(self.application.text_to_speech.utterances))
        self.assertEqual("Test", self.application.text_to_speech.utterances[0])

    def test_listen_after_talk_stops(self):
        listening_thread, talking_thread = self.threads

        in_speech_latch, exit_speech_latch, continue_speech_latch = listening_thread.listen(1, continue_latch=True)
        in_speech_latch.wait()

        exit_talk_latch = talking_thread.talk(["Test"])
        self.assertFalse(exit_talk_latch.wait(0.5))

        continue_speech_latch.set()
        exit_speech_latch.wait()

        # Ignoring speech while talking
        self.assertEqual(1, len(self.application.hypotheses))
        self.assertEqual('Test one two', self.application.hypotheses[0].transcript)
        self.assertEqual(1.0, self.application.hypotheses[0].confidence)

        _, exit_speech_latch = listening_thread.listen(1)
        exit_speech_latch.wait()

        self.assertEqual(1, len(self.application.hypotheses))
        self.assertEqual('Test one two', self.application.hypotheses[0].transcript)
        self.assertEqual(1.0, self.application.hypotheses[0].confidence)

        # Pick up speech again after talking
        _, exit_speech_latch, continue_speech_latch = listening_thread.listen(1, continue_latch=True)

        continue_speech_latch.set()
        self.application.text_to_speech.latch.set()
        exit_talk_latch.wait()
        exit_speech_latch.wait()

        sleep(0.1)

        self.assertEqual(2, len(self.application.hypotheses))
        self.assertEqual('Test one two', self.application.hypotheses[0].transcript)
        self.assertEqual(1.0, self.application.hypotheses[0].confidence)
        self.assertEqual('Test one two', self.application.hypotheses[1].transcript)
        self.assertEqual(1.0, self.application.hypotheses[1].confidence)

    def await(self, predicate, max=100, msg="predicate"):
        cnt = 0
        while not predicate() and cnt < max:
            sleep(0.01)
            cnt += 1

        if cnt == max:
            self.fail("Test timed out waiting for " + msg)


class ThreadsafeBoolean(object):
    def __init__(self):
        self._value = False
        self._lock = threading.Lock()

    @property
    def val(self):
        with self._lock:
            return self._value

    @val.setter
    def val(self, value):
        with self._lock:
            self._value = value

if __name__ == '__main__':
    unittest.main()