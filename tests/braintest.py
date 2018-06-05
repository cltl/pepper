import pepper
from threading import Thread
from time import time, sleep
from random import choice


class BrainTest(pepper.App):

    GREET = ["Hello", "Hi", "Hey There", "Greetings", "Good Day"]
    GREET_TIMEOUT = 30

    def __init__(self):
        super(BrainTest, self).__init__(pepper.ADDRESS)

        self._text_to_speech = self.session.service("ALAnimatedSpeech")

        # Speech Recognition
        self._microphone = pepper.PepperMicrophone(self.session)
        self._utterance = pepper.Utterance(self._microphone, self.on_utterance)
        self._speech_to_text = pepper.GoogleASR()

        # Face Recognition
        self._camera = pepper.PepperCamera(self.session, resolution=pepper.CameraResolution.VGA_640x480)
        self._openface = pepper.OpenFace()
        self._people_classifier = pepper.PeopleClassifier.from_directory(pepper.PeopleClassifier.LEOLANI)

        self._wolfram = pepper.Wolfram()

        self.speaking = False
        self._last_greeted_time = 0
        self._last_greeted_name = ""

        self._utterance.start()
        Thread(target=self._update_camera).start()

        self.log.info("Application Booted")

    def say(self, text, speed = 80):
        while self.speaking: sleep(0.1)

        self.speaking = True
        self.log.info(u"Leolani: '{}'".format(text))
        self._utterance.stop()
        self._text_to_speech.say(ur"\\rspd={}\\{}".format(speed, text))
        self._utterance.start()
        self.speaking = False

    def on_utterance(self, audio):
        self.log.info(u"Utterance {:3.3f}s".format(len(audio) / float(self._microphone.sample_rate)))

        hypotheses = self._speech_to_text.transcribe(audio)

        if hypotheses:
            self.on_transcript(*hypotheses[0])

    def on_transcript(self, transcript, confidence):
        self.log.info(u"[{:3.3%}] {}: '{}'".format(confidence, self._last_greeted_name, transcript))

        answer = self._wolfram.query(transcript)

        if answer:
            self.say(u"You asked {}. {}.".format(transcript, answer))

    def on_face(self, bounds, representation):
        name, confidence, distance = self._people_classifier.classify(representation)

        self.log.info(u"[{:3.3%}] Face - '{}'".format(confidence, name))

        if confidence > 0.9:
            if name != self._last_greeted_name or time() - self._last_greeted_time > self.GREET_TIMEOUT:
                self.say("{}, {}!".format(choice(self.GREET), name))
                self._last_greeted_name = name
                self._last_greeted_time = time()

    def _update_camera(self):
        while True:
            image = self._camera.get()

            face = self._openface.represent(image)
            if face: self.on_face(*face)
            sleep(0.5)


if __name__ == "__main__":
    BrainTest()