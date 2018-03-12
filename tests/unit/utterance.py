import pepper


class UtteranceTest(pepper.App):
    def __init__(self, address):
        super(UtteranceTest, self).__init__(address)

        self.microphone = pepper.PepperMicrophone(self.session)
        self.utterance = pepper.Utterance(self.microphone, self.on_utterance)
        self.asr = pepper.GoogleASR()

        self.utterance.start()

    def on_utterance(self, audio):
        print(self.asr.transcribe(audio))


if __name__ == "__main__":
    UtteranceTest(pepper.ADDRESS).run()