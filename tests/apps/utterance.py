from pepper.app import App
from pepper.speech.callback_microphone import PepperMicrophone, SystemMicrophone
from time import sleep


class EchoTest(App):
    def __init__(self, address):
        super(EchoTest, self).__init__(address)

        self.microphone = PepperMicrophone(self.session, self.on_audio)
        self.microphone2 = SystemMicrophone(16000, 1, self.on_audio)

        sleep(10)

    def on_audio(self, audio):
        print(len(audio))


if __name__ == "__main__":
    EchoTest(('192.168.137.159', 9559))