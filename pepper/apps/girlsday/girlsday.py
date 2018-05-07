import pepper
from pepper.apps.girlsday import knowledge
from random import choice
from time import time, sleep


class GirlsDayApp(pepper.SensorApp):

    OBJECT_CONFIDENCE_THRESHOLD = 0.6
    OBJECT_TIMEOUT = 300
    GREET_TIMEOUT = 60
    SPEECH_SPEED = 75

    def __init__(self, address):
        super(GirlsDayApp, self).__init__(address)

        self.wolfram = pepper.Wolfram()

        self.objects = {}
        self.object_classifier = pepper.ObjectClassifyClient()

        self.greeted_people = {}
        self.last_person = None
        self.last_new_person = 0

    def on_person_recognized(self, name):
        self.log.info("Recognized '{}'".format(name))

        # Greet Known Person if person switched or after timeout - Tell about objects she has seen
        if name != self.last_person or (name in self.greeted_people and time() - self.greeted_people[name] > self.GREET_TIMEOUT):
            if len(self.objects):
                self.say("{} {}, {}. {}".format(
                    choice(knowledge.GREET_KNOWN),
                    name,
                    choice(knowledge.TELL_KNOWN),
                    choice(knowledge.TELL_OBJECT).format(choice(self.objects.keys()))), self.SPEECH_SPEED)
            else:
                self.say("{} {}. {}".format(choice(knowledge.GREET_KNOWN), name, choice(knowledge.TELL_KNOWN)), self.SPEECH_SPEED)

            self.last_person = name
            self.greeted_people[name] = time()

    def on_person_new(self):
        self.log.info("New Person!")

        # Tell unknown person about the objects she has seen
        if len(self.objects):
            if time() - self.last_new_person > self.GREET_TIMEOUT:
                self.say('{} {}'.format(choice(knowledge.GREETINGS), choice(knowledge.TELL_OBJECT).format(choice(self.objects.keys()))))
                self.last_new_person = time()

            self.last_person = None

    def on_transcript(self, transcript, person):
        transcript = ' {} '.format(transcript)
        done = False

        self.log.info("{}: '{}'".format(person, transcript))

        # When Greeted, reply back with a greeting
        for greeting in [" hi ", " hello "]:
            if greeting in transcript.lower():
                self.say(choice(["Hi, yourself!", "Hello", "Hello Human", "Good day!", "Greetings", "It's a pleasure!"]))
                done = True
                break

        # On Affirmation, she takes it as a compliment!
        for affirmation in [" yes ", " yeah ", " correct ", " right ", " great ", " true ", " good ", " well done "]:
            if affirmation in transcript.lower():
                self.say(choice(["Nice!", "Cool!", "Great!", "Wow!", "Superduper!", "Amazing!"]))
                done = True
                break

        # On Negation, she tries to do her best
        for negation in [" no ", " nope ", " incorrect ", " wrong ", " false ", " bad "]:
            if negation in transcript.lower():
                self.say(choice(["Nawh, really? I'm doing my best!", "Excuse me!", "Better next time!", "Sorry"]))
                done = True
                break

        # Ask for objects!
        if not done and len(self.objects) >= 2:
            for query in ["What do you see", "What objects did you see", "What did you see"]:
                if query.lower() in transcript.lower():
                    self.say("I saw {} objects! Oh, I remember I saw a {}!".format(len(self.objects), choice(self.objects.keys())))
                    break
            if "which objects have you seen" in transcript.lower():
                object_list = self.objects.keys()
                self.say("I've seen a {} and a {}!".format(', a '.join(object_list[:-1]), object_list[-1]))

        # QnA Answering
        if not done:
            for question, answer in knowledge.QnA.items():
                if question.lower() in transcript.lower():
                    self.say("You asked: {}. {}".format(transcript, answer), self.SPEECH_SPEED)
                    done = True
                    break

        # Wolfram Alpha
        if not done:
            answer = self.wolfram.query(transcript)
            if answer:
                self.say("You asked {}. {}".format(
                    transcript, answer.encode('ascii', 'ignore').replace("Wolfram Alpha", "Leo Lani").split('.')[0]))

    def on_camera(self, image):
        super(GirlsDayApp, self).on_camera(image)

        # Classify Object
        self.classification = self.object_classifier.classify(image)

        confidence, labels = self.classification[0]
        if confidence > self.OBJECT_CONFIDENCE_THRESHOLD:
            label = choice(labels)

            if label not in self.objects or \
                    time() - self.objects[label][0] > self.OBJECT_TIMEOUT or \
                    confidence > self.objects[label][1] + 0.2:

                self.log.info("Recognized '{}' ({:3.1%})".format(label, confidence))

                # Report on Recognized Object with certain confidence
                if confidence < 0.75: sentence = choice(knowledge.OBJECT_NOT_SO_SURE)
                elif confidence < 0.9: sentence = choice(knowledge.OBJECT_QUITE_SURE)
                else: sentence = choice(knowledge.OBJECT_VERY_SURE)

                self.utterance.wait_for_silence()
                self.say(sentence.format(label), self.SPEECH_SPEED)
                self.objects[label] = time(), confidence
                sleep(10)


if __name__ == "__main__":
    GirlsDayApp(pepper.ADDRESS).run()
