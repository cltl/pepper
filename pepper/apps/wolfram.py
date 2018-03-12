import pepper

from random import choice

LAST_RESORT = [
    "I see",
    "Interesting",
    "Good to know",
    "I do not know, but I have a joke {insert joke}",
    "As the prophecy foretold",
    "But at what cost?",
    "So let it be written, ... so let it be done",
    "So ... it   has come to this",
    "That's just what he/she/they would've said",
    "Is this why fate brought us together?",
    "And thus, I die",
    "... just like in my dream",
    "Be that as it may, still may it be as it may be",
    "There is no escape from destiny",
    "Wise words by wise men write wise deeds in wise pen",
    "In this economy?",
    "and then the wolves came",
    "Many of us feel that way"
]

class WolframApp(pepper.App):
    def __init__(self, address):
        super(WolframApp, self).__init__(address)

        self.text_to_speech = self.session.service("ALAnimatedSpeech")
        self.speech_to_text_en = pepper.GoogleASR('en-GB')
        self.speech_to_text_nl = pepper.GoogleASR('nl-ML')

        self.wolfram = pepper.Wolfram()

        self.microphone = pepper.PepperMicrophone(self.session)
        self.utterance = pepper.Utterance(self.microphone, self.on_utterance)
        self.utterance.start()

        print("Application Booted")

    def on_utterance(self, audio):
        hypotheses_en = self.speech_to_text_en.transcribe(audio)
        hypotheses_nl = self.speech_to_text_nl.transcribe(audio)

        if hypotheses_en:
            question, confidence = hypotheses_en[0]

            if hypotheses_nl and hypotheses_nl[0][1] > confidence:
                self.say(u"I'm sorry, but I don't speak Dutch")
            else:
                print u"[{:3.0%}] {}".format(confidence, question),

                if confidence > 0.7:
                    answer = self.wolfram.query(question)

                    if answer:
                        self.say(u"You asked: {}. {}".format(question, answer))
                        print u" -> {}".format(answer),

                    else: self.say(choice(LAST_RESORT))

                else: self.say(u"You asked: {}, but I don't know the answer to that.".format(question))
                print("")

    def say(self, text):
        self.utterance.stop()
        self.text_to_speech.say(text)
        self.utterance.start()


if __name__ == "__main__":
    WolframApp(pepper.ADDRESS).run()