import pepper
from threading import Thread
import numpy as np


class PersonIdentificationApp(pepper.App):

    RESOLUTION = pepper.CameraResolution.VGA_320x240

    def __init__(self, address):
        super(PersonIdentificationApp, self).__init__(address)

        self.tts = self.session.service("ALAnimatedSpeech")

        self.people = pepper.load_data_set('lfw', 80)
        self.people.update(pepper.load_people())

        print("People in Database: {}".format(len(self.people)))

        self.cluster = pepper.PeopleCluster(self.people)
        self.cluster.performance()

        self.camera = pepper.PepperCamera(self.session, resolution=self.RESOLUTION)
        self.openface = pepper.OpenFace()

        self.microphone = pepper.PepperMicrophone(self.session)
        self.utterance = pepper.Utterance(self.microphone, self.on_utterance)
        self.name_asr = pepper.NameASR()

        self.person_name = None

        self._update_thread = Thread(target=self.update)
        self._update_thread.daemon = True
        self._update_thread.start()

        print("Application Running")

    def on_utterance(self, audio):
        hypothesis = self.name_asr.transcribe(audio)

        if hypothesis:
            name, confidence = hypothesis
            self.person_name = name
            self.utterance.stop()
        else:
            self.utterance.stop()
            self.say("Sorry, could you repeat that?")
            self.utterance.start()

    def on_person_new(self, confidence):
        self.say("I don't think we have met before. What is your name?")

        samples = []

        self.person_name = None
        self.utterance.start()

        while len(samples) < 10 or not self.person_name:
            image = self.camera.get()
            face = self.openface.represent(image)

            if face:
                bounds, representation = face
                samples.append(representation)

        self.utterance.stop()

        if self.person_name not in self.people:
            self.people[self.person_name] = np.array(samples)
            self.cluster = pepper.PeopleCluster(self.people)
            self.say("Nice to meet you, {}.".format(self.person_name))

    def on_person_recognise(self, name, confidence):
        self.say("Hello, {}".format(name))

    def update(self):
        while True:
            image = self.camera.get()
            face = self.openface.represent(image)

            if face:
                bounds, representation = face
                name, score = self.cluster.classify(representation)

                if score > 0.25: self.on_person_recognise(name, score)
                elif score < 0.01: self.on_person_new(score)
                else: print(name, score)

    def say(self, text):
        self.tts.say(text)


if __name__ == "__main__":
    PersonIdentificationApp(pepper.ADDRESS).run()