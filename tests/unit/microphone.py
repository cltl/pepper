from pepper import ADDRESS, App, PepperMicrophone
from time import sleep


class MicrophoneTest(App):
    def __init__(self, address):
        """
        Test Pepper Microphone by Writing Output to .wav File

        Parameters
        ----------
        address: (str, int)
            tuple of (<ip>, <port>)
        """
        super(MicrophoneTest, self).__init__(address)

        self.microphone = PepperMicrophone(self.session, [self.on_audio])
        self.microphone.start()

    def on_audio(self, samples):
        sleep(0.05)


if __name__ == "__main__":
    app = MicrophoneTest(ADDRESS).run()
