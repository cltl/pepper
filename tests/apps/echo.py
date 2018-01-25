from pepper.app import App
from pepper.speech.microphone import PepperMicrophone, SystemMicrophone
from pepper.speech.utterance import Utterance
from pepper.speech.recognition import GoogleRecognition


class EchoTest(App):
    def __init__(self, address):
        super(EchoTest, self).__init__(address)

        self.speech = self.session.service("ALAnimatedSpeech")

        # self.microphone = SystemMicrophone(16000, 1)
        self.microphone = PepperMicrophone(self.session)
        self.utterance = Utterance(self.microphone, self.on_utterance)
        self.recognition = GoogleRecognition()

        self.utterance.start()

        print("\nBooted Echo App")

    def on_utterance(self, audio):
        hypotheses = self.recognition.transcribe(audio)

        if hypotheses:
            transcript, confidence = hypotheses[0]
            print("[{:3.0%}] {}".format(confidence, transcript))
            self.say(transcript)

        elif len(audio) > 2 * self.microphone.sample_rate:
            self.say("Sorry, I didn't hear you properly. :(")

    def say(self, text):
        self.utterance.stop()
        self.speech.say(text)
        self.utterance.start()


if __name__ == "__main__":
    app = EchoTest(('192.168.137.159', 9559))
    app.run()