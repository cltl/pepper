from pepper import ADDRESS, App, PepperMicrophone, SystemMicrophone
from pepper.input.microphone import PepperMicrophoneModule
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

        self.microphone = PepperMicrophoneModule(self.session)
        print("Microphone Test Started")


if __name__ == "__main__":
    app = MicrophoneTest(ADDRESS).run()
