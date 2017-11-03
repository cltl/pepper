from pepper.app import App
from pepper.event.people import LookingAtRobotEvent, FaceDetectedEvent

from pepper.speech.microphone import PepperMicrophone
from pepper.speech.recognition import GoogleStreamedRecognition
from pepper.knowledge.wolfram import Wolfram
from pepper.knowledge.greetings import CATCH_ATTENTION, SIMPLE_GREETING

from time import sleep, time
from random import choice


WOLFRAM_NO_RESULT = [
    "I have no clue, sorry",
    "I don't know",
    "You should look it up yourself!",
    "Google it!",
    "How would I know? I am a robot!"
]


class BachelorDay(App):
    def __init__(self, address):
        super(BachelorDay, self).__init__(address)

        self.microphone = PepperMicrophone(self.session)
        self.recognition = None
        self.wolfram = Wolfram()

        self.listening = False
        self.busy = False

        self.speech = self.session.service("ALAnimatedSpeech")
        self.events.append(FaceDetectedEvent(self.session, self.on_face))
        self.events.append(LookingAtRobotEvent(self.session, self.on_look))

    def on_face(self, time, faces, recognition):
        # Call for attention
        if not self.busy:
            animation = choice(CATCH_ATTENTION['ANIMATIONS'])
            text = choice(CATCH_ATTENTION['TEXT'])
            self.speech.say("^start(%s) %s ^stop(%s)").format(animation, text, animation)
            sleep(15)

    def on_look(self, person, score):
        if not self.busy and not self.listening:
            animation = choice(SIMPLE_GREETING['ANIMATIONS'])
            text = choice(SIMPLE_GREETING['TEXT'])
            self.speech.say("^start(%s) %s ^stop(%s)").format(animation, text, animation)
            sleep(4)

            self.speech.say("I'm listening!")
            self.listen()
            sleep(5)

    def on_speech(self, hypotheses, final):
        question = hypotheses[0][0]

        if final:
            self.busy = True
            self.recognition.stop()
            print u"\rQ: {}?".format(question)
            self.speech.say(u"You asked: {}".format(question))
            answer = self.wolfram.query(question)
            if answer:
                answer = answer.replace("Wolfram Alpha", "Leo Lani")
                print(u"A: {}\n".format(answer))
                self.speech.say(answer)
            else:
                answer = choice(WOLFRAM_NO_RESULT)
                print(u"A: {}\n".format(answer))
                self.speech.say(answer)
                sleep(4)
            self.busy = False
        else:
            print "\rQ: {}".format(question),

    def listen(self, duration = 10):
        self.listening = True
        self.recognition = GoogleStreamedRecognition(self.microphone, self.on_speech)
        sleep(duration)
        self.recognition.stop()
        self.listening = False


if __name__ == "__main__":
    app = BachelorDay(["192.168.1.103", 9559])
    app.run()
