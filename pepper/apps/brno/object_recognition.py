import pepper
import numpy as np
from scipy.misc import imsave

from threading import Thread
from random import choice
from time import sleep, time


def enumerate_objects(dictionary):
    string = ""
    for cls, count in dictionary.items():
        string += "{} {}".format(count, cls) + ("s, " if count > 1 else ", ")
    object_string = string[:-2]

    if ', ' in object_string:
        k = object_string.rfind(',')
        string = object_string[:k] + ' and' + object_string[k + 1:]

    return string

class ObjectRecognitionApp(pepper.App):

    GREET = ["Hello", "Hi", "Hey there", "Greetings", "Good day", "Nice to see you", "It's a pleasure", "Hey"]

    RESOLUTION = pepper.CameraResolution.VGA_640x480
    SCORE_THRESHOLD = 0.7
    FACE_THRESHOLD = 0.8

    FACE_TIMEOUT = 60

    def __init__(self):
        super(ObjectRecognitionApp, self).__init__(pepper.ADDRESS)

        self.text_to_speech = self.session.service("ALAnimatedSpeech")

        self.camera = pepper.PepperCamera(self.session, resolution=self.RESOLUTION)
        self.coco = pepper.CocoClassifyClient()
        self.inception = pepper.ObjectClassifyClient()

        self.openface = pepper.OpenFace()
        self.people_classifier = pepper.PeopleClassifier.from_directory(pepper.PeopleClassifier.LEOLANI)

        self.last_name = ""
        self.last_name_time = 0

        self.last_objects = {}
        self.all_objects = {}

        Thread(target=self.update).start()
        print("Application Booted")

    def say(self, text, speed=80):
        self.log.info(u"Leolani: '{}'".format(text))
        self.text_to_speech.say(ur"\\rspd={}\\{}".format(speed, text))

    def on_image(self, image):
        height, width, channels = image.shape
        classes, scores, boxes = self.coco.classify(image)

        # Update Last Objects
        self.last_objects = {}

        for cls, scr, box in zip([cls['name'] for cls in classes], scores, boxes):
            if scr > self.SCORE_THRESHOLD:

                x0 = int(box[1] * width)
                y0 = int(box[0] * height)
                x1 = int(box[3] * width)
                y1 = int(box[2] * height)
                image_slice = image[y0:y1, x0:x1]

                imsave("{}.png".format(cls), image_slice)

                scr_inception, cls_inception = self.inception.classify(image_slice)[0]

                if cls != 'person' and scr_inception > 0.5 :
                    print(scr, cls, scr_inception, cls_inception)

                if not cls in self.last_objects:
                    self.last_objects[cls] = 1
                else:
                    self.last_objects[cls] += 1

        for cls, count in self.last_objects.items():
            if not cls in self.all_objects:
                self.all_objects[cls] = count
            elif self.all_objects[cls] < count:
                self.all_objects[cls] = count

        face = self.openface.represent(image)
        if face:
            bounds, representation = face
            name, confidence, distance = self.people_classifier.classify(representation)

            print(name, confidence)

            if confidence > self.FACE_THRESHOLD:
                if name != self.last_name or time() - self.last_name_time > self.FACE_TIMEOUT:

                    self.say("{}, {}!".format(choice(self.GREET), name))
                    self.last_name = name
                    self.last_name_time = time()

                    if self.last_objects:
                        self.say("I see " + enumerate_objects(self.last_objects) + ".")

                    if self.all_objects:
                        self.say("Since I was looking, I have seen " + enumerate_objects(self.all_objects) + ".")


    def update(self):
        while True:
            self.on_image(self.camera.get())


if __name__ == "__main__":
    ObjectRecognitionApp()