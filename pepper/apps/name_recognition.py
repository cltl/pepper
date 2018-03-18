import pepper
from pepper.language.name_recognition import NameRecognition


class NameRecognitionApp(pepper.FlowApp):
    def __init__(self, address):
        super(NameRecognitionApp, self).__init__(address)

        self.asr = pepper.GoogleASR(max_alternatives=5)
        self.name_recognition = NameRecognition()

    def on_utterance(self, audio):
        hypotheses = self.asr.transcribe(audio)

        if hypotheses:
            for transcript, confidence in hypotheses:
                self.log.info('[{:3.1%}] {}'.format(confidence, transcript))

                transcript = self.name_recognition.recognize(transcript)

                if '{}' in transcript:
                    name, name_confidence = pepper.NameASR(hints=(transcript,)).transcribe(audio)
                    transcript = transcript.format(name)
                    print(transcript)
                    self.say("You said: {}.".format(transcript))
                    break

if __name__ == "__main__":
    NameRecognitionApp(pepper.ADDRESS).run()