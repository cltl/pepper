from pepper.app import App
from pepper.event.people import LookingAtRobotEvent, FaceDetectedEvent

from pepper.speech.microphone import PepperMicrophone
from pepper.speech.recognition import GoogleStreamedRecognition
from pepper.knowledge.wolfram import Wolfram
from pepper.knowledge.greetings import CATCH_ATTENTION, SIMPLE_GREETING

import pepper.knowledge.vu_bachelors as bachelors

from pepper.knowledge.general_questions import general_questions

from time import sleep, time
from random import choice

############ CONSTANTS ############

WOLFRAM_NO_RESULT = [
    "I have no clue, sorry",
    "I don't know",
    "You should look it up yourself!",
    "Google it!",
    "How would I know? I am a robot!",
    "I have no idea",
    "That is a very complex question for a simple robot like me"
]

ASK_FOR_QUESTION = [
    "I'm listening",
    "Shoot me a question",
    "What would you like to know?",
    "What's your question?",
    "I am ready for your question",
    "Ask me"
    "Let's hear your question"
]

SECONDS_BETWEEN_GREETINGS = 60

VOICE_SPEED = 80
SAY_SPEED = "\RSPD=" + str(VOICE_SPEED) + "\ "

####################################

class BachelorDay(App):
    def __init__(self, address):
        super(BachelorDay, self).__init__(address)

        self.microphone = PepperMicrophone(self.session)
        self.recognition = None
        self.wolfram = Wolfram()

        self.listening = False
        self.busy = False
        self.lastGreetingTime = 0

        self.speech = self.session.service("ALAnimatedSpeech")
        self.events.append(FaceDetectedEvent(self.session, self.on_face))
        self.events.append(LookingAtRobotEvent(self.session, self.on_look))

    def on_face(self, time, faces, recognition):
        # # Call for attention
        # if not self.busy:
        #     self.busy = True
        #     animation = choice(CATCH_ATTENTION['ANIMATIONS'])
        #     text = choice(CATCH_ATTENTION['TEXT'])
        #     self.speech.say("^start(%s) %s ^stop(%s)").format(animation, text, animation)
        #     sleep(15)
        #     self.busy = False
        pass

    def on_look(self, person, score):
        # Person is already looking at robot, so do a simple greeting
        if not self.busy and not self.listening:
            self.busy = True
            if time() - self.lastGreetingTime > SECONDS_BETWEEN_GREETINGS :
                self.lastGreetingTime = time()
                animation = choice(SIMPLE_GREETING['ANIMATIONS'])
                text = choice(SIMPLE_GREETING['TEXT'])
                self.speech.say("^start({}) {} ^stop({})".format(animation, text, animation))
                sleep(2)

            text = choice(ASK_FOR_QUESTION)
            self.speech.say(text)
            self.listen()
            sleep(5)
            self.busy = False

    def on_speech(self, hypotheses, final):
        question = hypotheses[0][0]

        if final:
            self.busy = True
            self.recognition.stop()

            # Question has been recognised #
            print u"\rQ: {}?".format(question)
            self.speech.say(u"You asked: {}".format(question))

            answer = general_questions(question)

            if answer:
                self.speech.say(answer)
                print("A: {}\n".format(answer))
            else:
                # Bachelors #
                found_bachelor_match = False
                for bachelor in bachelors.ONE_LINER.keys():
                    for bachelor_tag in bachelor:
                        if bachelor_tag in question.lower():
                            print("A: {}\n".format(bachelor[0]))
                            self.speech.say("I will now talk about the bachelor {}".format(bachelor[0]))
                            self.speech.say("{}{}".format(SAY_SPEED, bachelors.ONE_LINER[bachelor]))
                            found_bachelor_match = True
                            break

                if not found_bachelor_match:
                    # Wolfram Alpha #
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

    def listen(self, duration = 15):
        self.listening = True
        self.recognition = GoogleStreamedRecognition(self.microphone, self.on_speech)
        sleep(duration)
        self.recognition.stop()
        self.listening = False


if __name__ == "__main__":
    app = BachelorDay(["192.168.1.103", 9559])
    app.run()
