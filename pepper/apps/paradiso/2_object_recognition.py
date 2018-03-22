import pepper

from random import choice
from time import time


class ObjectRecognitionApp(pepper.SensorApp):

    PERSON_GREET_TIMEOUT = 120
    CONFIDENCE_THRESHOLD = 0.5
    OBJECT_TIMEOUT = 300

    KNOWN_PERSON = [
        "Nice to see you again!",
        "It has been a long time!",
        "I'm glad we see each other again!",
        "You came back!",
        "At last!",
        "I was thinking about you!"
    ]

    TELL_OBJECT = [
        "Guess what, I saw a {}",
        "Would you believe, I just saw a {}",
        "Did you know there's a {} here?",
        "I'm happy, I saw a {}"
    ]

    GREET = ["Hello", "Hi", "Hey There", "Greetings"]

    NOT_SO_SURE = [
        "I'm not sure, but I see a {}!",
        "I don't think I'm correct, but it that a {}?",
        "Would that be a {}?",
        "I could be wrong, but I think I see a {}",
        "hmmmm, Just guessing, a {}?",
        "Haha, is that a {}?",
        "It's not clear to me, but would that be a {}?"
    ]

    QUITE_SURE = [
        "I think that is a {}!",
        "That's a {}, if my eyes are not fooling me!",
        "I think I can see a {}!",
        "I can see a {}!",
    ]

    VERY_SURE = [
        "That's a {}, I'm one hundred percent sure!",
        "I see it clearly, that is a {}!",
        "Yes, a {}!",
        "Awesome, that's a {}!"
    ]

    def __init__(self, address):
        super(ObjectRecognitionApp, self).__init__(address, camera_frequency=1)

        self.objects = {}
        self.object_classifier = pepper.ObjectClassifyClient()
        self.bottom_camera = pepper.PepperCamera(self.session, pepper.CameraTarget.BOTTOM)

        self.last_object = None
        self.greeted_people = {}

    def on_camera(self, image):
        super(ObjectRecognitionApp, self).on_camera(image)

        self.classify(image)
        self.classify(self.bottom_camera.get())

    def classify(self, image):
        confidence, labels = self.object_classifier.classify(image)[0]

        if confidence > self.CONFIDENCE_THRESHOLD:
            label = choice(labels)

            if label not in self.objects or \
                    time() - self.objects[label][0] > self.OBJECT_TIMEOUT or \
                    confidence > self.objects[label][1]:

                score = (confidence - self.CONFIDENCE_THRESHOLD) / (1 - self.CONFIDENCE_THRESHOLD)

                self.log.info("[{:3.1%}] {}".format(score, label))

                if score < 1.0/5.0: sentence = choice(self.NOT_SO_SURE)
                elif score < 1.0/2.0: sentence = choice(self.QUITE_SURE)
                else: sentence = choice(self.VERY_SURE)

                self.say(sentence.format(label))
                self.objects[label] = time(), confidence

                self.last_object = label

    def on_person_recognized(self, name):
        if name not in self.greeted_people or time() - self.greeted_people[name] > self.PERSON_GREET_TIMEOUT:
            if self.last_object:
                self.say("{} {}, {}. {}!".format(
                    choice(self.GREET),
                    name,
                    choice(self.KNOWN_PERSON),
                    choice(self.TELL_OBJECT).format(self.last_object)))
                self.greeted_people[name] = time()

if __name__ == "__main__":
    ObjectRecognitionApp(pepper.ADDRESS).run()
