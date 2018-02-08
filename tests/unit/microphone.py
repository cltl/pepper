from pepper import ADDRESS, App, PepperMicrophone
import wave


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

        self.wave = wave.open("microphonetest.wav", 'wb')
        self.wave.setframerate(self.microphone.sample_rate)
        self.wave.setnchannels(1)
        self.wave.setsampwidth(2)

        self.total_samples = 0

    def on_audio(self, samples):
        self.total_samples += samples
        self.wave.writeframes(samples)
        print "\rWrote {:3.1f} seconds of audio".format(self.total_samples / self.microphone.sample_rate),

    def stop(self):
        super(MicrophoneTest, self).stop()
        self.wave.close()


if __name__ == "__main__":
    app = MicrophoneTest(ADDRESS)