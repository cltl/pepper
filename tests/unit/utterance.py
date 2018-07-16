import pepper


class UtteranceTest(pepper.App):
    def __init__(self, address):
        super(UtteranceTest, self).__init__(address)

        self.microphone = pepper.PepperMicrophone(self.session, [], pepper.PepperMicrophoneMode.LEFT)
        self.utterance = pepper.Utterance(self.microphone, self.on_utterance)
        self.utterance.start()

    def on_audio(self, audio):
        print(self.utterance.activation())

    def on_utterance(self, audio):
        print("Utterance {:3.2f}s!".format(len(audio) / float(self.microphone.sample_rate)))


if __name__ == "__main__":
    UtteranceTest(pepper.ADDRESS).run()