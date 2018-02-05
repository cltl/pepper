from pepper.app import App
from pepper.speech.microphone import PepperMicrophone, SystemMicrophone
from pepper.speech.utterance import Utterance
from pepper.speech.recognition import GoogleRecognition
from pepper.output.led import Led

from threading import Thread
from time import sleep

from scipy.io import wavfile


class EchoTest(App):
    def __init__(self, address):
        super(EchoTest, self).__init__(address)

        self.led = Led(self.session)

        self.speech = self.session.service("ALAnimatedSpeech")

        # self.microphone = SystemMicrophone(16000, 1)
        self.microphone = PepperMicrophone(self.session)
        self.utterance = Utterance(self.microphone, self.on_utterance)
        self.recognition = GoogleRecognition()

        self.utterance.start()

        Thread(target=self.voice_activation).start()

        print("\nBooted Echo App")

    def voice_activation(self):
        while True:
            value = float(self.utterance.activation())
            self.led.set((value if value > self.utterance.VOICE_THRESHOLD else 0, 0, value))
            sleep(0.2)

    def on_utterance(self, audio):
        print("Utterance Detected!")

        hypotheses = self.recognition.transcribe(audio)

        if hypotheses:
            transcript, confidence = hypotheses[0]
            print("[{:3.0%}] {}".format(confidence, transcript))
            self.say(transcript)

            ROOT = r"C:\Users\Bram\Documents\Pepper\data\speech\samples"
            wavfile.write(r"{}\{}.wav".format(ROOT, transcript), 16000, audio)

        # elif len(audio) > 2 * self.microphone.sample_rate:
        #     self.say("Sorry, I didn't hear you properly. :(")

    def say(self, text):
        self.utterance.stop()
        self.speech.say(text)
        self.utterance.start()


if __name__ == "__main__":
    app = EchoTest(('192.168.137.49', 9559))
    app.run()