from pepper.app import App
from pepper.speech.recognition import *
from pepper.speech.microphone import PepperMicrophone
from pepper.event.people import FaceDetectedEvent
from time import sleep

class EchoApp(App):

    LISTEN_DURATION = 5

    def __init__(self, address, recognition):
        """
        Parameters
        ----------
        address: (str, int)
        recognition: Recognition
        """
        super(EchoApp, self).__init__(address)

        self.speech = self.session.service("ALAnimatedSpeech")

        self.recognition = recognition
        self.microphone = PepperMicrophone(self.session)
        self.listening = False

        self.resources.append(FaceDetectedEvent(self.session, self.on_face))

    def on_face(self, time, faces, recognition):
        if not self.listening:
            self.listening = True
            self.speech.say("Speak, human!")
            print("Get Audio")
            audio = self.microphone.get(self.LISTEN_DURATION)
            print("Transcribe Audio")

            hypotheses = self.recognition.transcribe(audio)

            for transcript, confidence in hypotheses:
                print(u"[{:3.0%}] {}".format(confidence, transcript))

            transcript, confidence = hypotheses[0]

            self.speech.say(transcript)
            sleep(3)
            self.listening = False


if __name__ == "__main__":
    EchoApp(("192.168.1.103", 9559), KaldiRecognition()).run()


