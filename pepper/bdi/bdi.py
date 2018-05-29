import pepper

import requests
import pyping

from threading import Thread
from datetime import datetime
from time import time, sleep


class Events:
    def on_utterance(self, audio, confidence):
        pass

    def on_transcript(self, transcripts, confidences):
        pass

    def on_camera_image(self, image):
        pass

    def on_person(self, bounds, representation):
        pass

    def on_person_new(self, bounds, representation, confidence):
        pass

    def on_person_recognized(self, name, bounds, representation, confidence):
        pass

    def on_object(self, synset, confidence):
        pass

    def on_brain_conflict(self, entity, attribute, confidence):
        pass

    def on_brain_hunger(self, entity, attribute):
        pass

    def on_syntax_error(self, description):
        pass

    def on_semantic_error(self, description):
        pass


class Intention(Events):
    def __init__(self):
        self._belief = None

    @property
    def belief(self):
        """
        Returns
        -------
        belief: Belief
        """
        return self._belief

    @belief.setter
    def belief(self, value):
        self._belief = value


class TellPlaceIntention(Intention):
    def on_transcript(self, transcripts, confidences):

        place = self.belief.place

        for transcript in transcripts:
            if "city" in transcript.lower():
                self.belief.say("We're now in the city of {}".format(place['city']))
                break
            elif "country" in transcript.lower():
                self.belief.say("The country code is {}".format(place['country']))
                break
            elif "region" in transcript.lower():
                self.belief.say("We're in the region of {}".format(place['region']))
                break


class Belief(pepper.App, Events):

    NAME = "Leolani"
    CAMERA_RESOLUTION = pepper.CameraResolution.VGA_640x480
    CAMERA_FRAMERATE = 2

    def __init__(self, intention):
        super(Belief, self).__init__(pepper.ADDRESS)
        self._intention = intention
        self.intention.belief = self

        # State
        self._speaking = False
        self._thinking = False

        # Text to Speech & Speech to Text
        self.log.info("Initializing Text-to-Speech and Speech-to-Text Services")
        self._text_to_speech = self.session.service("ALAnimatedSpeech")
        self._speech_to_text = pepper.GoogleASR()

        # Audio Stream
        self.log.info("Initializing Microphone and Voice Activity Detection Services")
        self._microphone = pepper.PepperMicrophone(self.session)
        self._utterance = pepper.Utterance(self._microphone, self._on_utterance)

        # Camera Stream
        self.log.info("Initializing Camera Stream")
        self._camera = pepper.PepperCamera(self.session, resolution=Belief.CAMERA_RESOLUTION)
        self._camera_thread = Thread(target=self._update)

        # Face Detection
        self.log.info("Initializing OpenFace")
        self._open_face = pepper.OpenFace()

        # Start processes
        self._utterance.start()
        self._camera_thread.start()

        self.log.info("..:: Booted Application ::..")

    @property
    def intention(self):
        """
        Get Current Intention

        Returns
        -------
        intention: Intention
            Current Intention
        """
        return self._intention

    @intention.setter
    def intention(self, value):
        """
        Set Current Intention

        Parameters
        ----------
        value: Intention
        """
        self._intention = value
        self._intention.belief = self

    @property
    def online(self):
        return pyping.ping('{}:{}'.format(*self.address)) == 0

    @property
    def place(self):
        return requests.get('http://ipinfo.io/json').json()

    @property
    def time(self):
        return datetime.now()

    @property
    def speaking(self):
        return self._speaking

    @property
    def thinking(self):
        return self._thinking

    @property
    def hearing(self):
        return self._utterance.activation()

    def say(self, text, speed = 80):
        while self._speaking: sleep(0.1)
        self.log.info("{}: {}".format(Belief.NAME, text))

        self._speaking = True
        self._utterance.stop()
        self._text_to_speech.say(r"\\rspd={}\\{}".format(speed, text))
        self._utterance.start()
        self._speaking = False

    def on_utterance(self, audio, confidence):
        self.log.info("on_utterance[{:3.3%}]: {:3.3f}s".format(
            confidence, len(audio) / float(self._microphone.sample_rate)))
        self.intention.on_utterance(audio, confidence)

    def on_transcript(self, transcripts, confidences):
        self.log.info("on_transcript[{:3.3%}]: {}".format(confidences[0], transcripts[0]))
        self.intention.on_transcript(transcripts, confidences)

    def on_camera_image(self, image):
        self.intention.on_camera_image(image)

    def on_person(self, bounds, representation):
        self.intention.on_person(bounds, representation)

    def on_person_new(self, bounds, representation, confidence):
        self.log.info("on_person_new[{:3.3%}]".format(confidence))
        self.intention.on_person_new(bounds, representation, confidence)

    def on_person_recognized(self, name, bounds, representation, confidence):
        self.log.info("on_person_recognized[{:3.3%}] {}".format(confidence, name))
        self.intention.on_person_recognized(name, bounds, representation, confidence)

    def on_object(self, synset, confidence):
        self.log.info("on_object[{:3.3%}] {}".format(confidence, synset))
        self.intention.on_object(synset, confidence)

    def on_brain_conflict(self, entity, attribute, confidence):
        self.log.info("on_brain_conflict[{:3.3%}] {}:{}".format(confidence, entity, attribute))
        self.intention.on_brain_conflict(entity, attribute, confidence)

    def on_brain_hunger(self, entity, attribute):
        self.log.info("on_brain_hunger {}:{}".format(entity, attribute))
        self.intention.on_brain_hunger(entity, attribute)

    def on_syntax_error(self, description):
        self.log.info("on_syntax_error: {}".format(description))
        self.intention.on_syntax_error(description)

    def on_semantic_error(self, description):
        self.log.info("on_semantic_error: {}".format(description))
        self.intention.on_semantic_error(description)

    def _on_utterance(self, audio):
        hypotheses = self._speech_to_text.transcribe(audio)
        self.on_utterance(audio, 1)

        if hypotheses:
            transcripts = [hypothesis[0] for hypothesis in hypotheses]
            confidences = [hypothesis[1] for hypothesis in hypotheses]
            self.on_transcript(transcripts, confidences)

    def _update(self):
        while True:
            # On Camera Image Event
            t0 = time()
            image = self._camera.get()
            self.on_camera_image(image)

            # On Face Event
            face = self._open_face.represent(image)
            if face: self.on_person(*face)

            # TODO: On Person Recognize Event

            # TODO: On Person New Event

            # TODO: On Object Event

            sleep(1.0 / Belief.CAMERA_FRAMERATE)  # Important to keep the rest working :)


if __name__ == "__main__":
    intention = TellPlaceIntention()
    Belief(intention).run()
